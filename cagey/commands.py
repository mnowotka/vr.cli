from __future__ import print_function

import pprint
import argparse
import itertools

import six
from jaraco.util import cmdline

from . import models


class FilterExcludeAction(argparse.Action):
	def __call__(self, parser, namespace, values, option_string=None):
		namespace.filter.exclusions.append(values)

class Swarm(cmdline.Command):
	@classmethod
	def add_arguments(cls, parser):
		parser.add_argument('filter', type=models.SwarmFilter)
		parser.add_argument('tag')
		parser.add_argument('-x', '--exclude', action=FilterExcludeAction)

	@classmethod
	def run(cls, args):
		swarms = models.Swarm.load_all(args.vr)
		matched = list(args.filter.matches(swarms))
		print("Matched", len(matched), "apps")
		pprint.pprint(matched)
		models.countdown("Reswarming in {} sec")
		[swarm.dispatch(args.tag) for swarm in matched]


class Builder(object):
	@classmethod
	def build(cls, vr, app, tag):
		vr.assemble(app, tag)


class Build(Builder, cmdline.Command):
	@classmethod
	def add_arguments(cls, parser):
		parser.add_argument('app')
		parser.add_argument('tag')

	@classmethod
	def run(cls, args):
		cls.build(args.vr, args.app, args.tag)


class RebuildAll(Builder, cmdline.Command):
	@classmethod
	def add_arguments(cls, parser):
		parser.add_argument('filter', type=models.SwarmFilter)
		parser.add_argument('-x', '--exclude', action=FilterExcludeAction)

	@classmethod
	def run(cls, args):
		swarms = models.Swarm.load_all(args.vr)
		swarms = list(args.filter.matches(swarms))
		print("Matched", len(swarms), "apps")
		pprint.pprint(swarms)
		models.countdown("Rebuilding in {} sec")
		for build in cls.unique_builds(swarms):
			cls.build(vr=args.vr, **build)

		six.moves.input("Hit enter to continue once builds are done...")
		for swarm in swarms:
			args.vr.cut()

		print('swarming new releases...')
		for swarm in swarms:
			swarm.dispatch(args.vr)

	@classmethod
	def unique_builds(cls, swarms):
		items = [
			models.HashableDict(swarm.build)
			for swarm in swarms
		]
		return set(items)


class ListProcs(cmdline.Command):

	@classmethod
	def add_arguments(cls, parser):
		parser.add_argument('filter', type=models.SwarmFilter)

	@classmethod
	def run(cls, args):
		swarmtmpl = '{} [{}]'
		proctmpl = '  {host:<22}  {port:<5}  {statename:<9}  {description}'

		all_swarms = models.Swarm.load_all(args.vr.home)
		swarm_names = [s.name for s in args.filter.matches(all_swarms)]

		our_procs = [
			p for p in models.Velociraptor.procs()
			if p['swarmname'] in swarm_names
		]

		kfunc = lambda proc: (proc['swarmname'], proc['tag'])
		our_procs = sorted(our_procs, key=kfunc)
		proc_groups = itertools.groupby(our_procs, key=kfunc)

		for ktpl, procs in proc_groups:
			print()
			print(swarmtmpl.format(*ktpl))
			for proc in procs:
				print(proctmpl.format(**proc))

class ListSwarms(cmdline.Command):

	@classmethod
	def add_arguments(cls, parser):
		parser.add_argument('filter', type=models.SwarmFilter, nargs='?')

	@classmethod
	def run(cls, args):
		all_swarms = models.Swarm.load_all(args.vr)
		filtered_swarms = all_swarms
		if args.filter:
			filtered_swarms = args.filter.matches(all_swarms)
		[print(swarm) for swarm in sorted(filtered_swarms)]


class Uptests(cmdline.Command):

	@classmethod
	def run(cls, args):
		resp = args.vr.load('/api/uptest/latest').json()
		procs = resp['results']
		for proc_name in procs:
			ut_results = procs[proc_name]
			for result in ut_results:
				if not result['passed']:
					print(proc_name, "failed on", result['uptest'])


def handle_command_line():
	parser = argparse.ArgumentParser()
	parser.add_argument('--url',
		help="Velociraptor URL (defaults to https://deploy, resolved)")
	parser.add_argument('--username',
		help="Override the username used for authentication")
	cmdline.Command.add_subparsers(parser)
	args = parser.parse_args()
	models.Velociraptor.username = args.username
	args.vr = models.Velociraptor(args.url, args.username)
	args.action.run(args)
