from __future__ import print_function

import argparse
import getpass
import re
import pprint
import urlparse
import io
import time
import sys
import datetime

import requests
import keyring
import lxml.html

session = requests.session()
username = getpass.getuser()
password = keyring.get_password('YOUGOV.LOCAL', username) or getpass.getpass()
vr_base = 'https://deploy.yougov.net'

class SwarmFilter(unicode):
	exclusions = []

	def matches(self, names):
		return filter(self.match, names)

	def match(self, name):
		return (
			not any(re.search(exclude, name, re.I)
				for exclude in self.exclusions)
			and re.match(self, name)
		)

class FilterExcludeAction(argparse.Action):
	def __call__(self, parser, namespace, values, option_string=None):
		namespace.filter.exclusions.append(values)

def get_args():
	parser = argparse.ArgumentParser()
	parser.add_argument('filter', type=SwarmFilter)
	parser.add_argument('tag')
	parser.add_argument('-x', '--exclude', action=FilterExcludeAction)
	return parser.parse_args()

def auth():
	resp = session.get(vr_base)
	if 'baton' in resp.text:
		resp = session.post(resp.url, data=dict(username=username,
			password=password))
	return resp

def get_swarms(home):
	swarm_pat = re.compile('<option value="(?P<path>/swarm/\d+/)">(?P<name>.*?)</option>')
	matches = swarm_pat.finditer(home.text)
	swarms = {match.group('name'): match.group('path') for match in matches}
	if not swarms:
		print("No swarms found at", home.url, file=sys.stderr)
		print("Response was", home.text, file=sys.stderr)
		raise SystemExit(1)
	return swarms

def countdown(template):
	now = datetime.datetime.now()
	delay = datetime.timedelta(seconds=5)
	deadline = now + delay
	remaining = deadline - datetime.datetime.now()
	while remaining:
		remaining = deadline - datetime.datetime.now()
		remaining = max(datetime.timedelta(), remaining)
		msg = template.format(remaining.total_seconds())
		print(msg, end=' '*10)
		sys.stdout.flush()
		time.sleep(.1)
		print('\b'*80, end='')
		sys.stdout.flush()
	print()

def get_lxml_opener(session):
	"""
	Given a requests session, return an opener suitable for passing to LXML
	"""
	return lambda method, url, values: session.request(url=url, method=method,
		data=values)

def swarm(path, tag):
	url = urlparse.urljoin(vr_base, path)
	resp = session.get(url)
	page = lxml.html.fromstring(resp.text, base_url=resp.url)
	form = page.forms[0]
	form.fields.update(tag=tag)
	return lxml.html.submit_form(form,
		open_http=get_lxml_opener(session))

def reswarm():
	args = get_args()
	swarms = get_swarms(auth())
	matched_names = list(args.filter.matches(swarms))
	print("Matched", len(matched_names), "apps")
	pprint.pprint(matched_names)
	countdown("Reswarming in {} sec")
	[swarm(swarms[name], args.tag) for name in matched_names]

if __name__ == '__main__':
	reswarm()
