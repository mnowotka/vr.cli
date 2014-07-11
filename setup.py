#!/usr/bin/env python
# Generated by jaraco.develop (https://bitbucket.org/jaraco/jaraco.develop)
import setuptools

with open('README') as stream:
	long_description = stream.read()

setup_params = dict(
	name='vr.cli',
	use_hg_version=dict(increment='0.1'),
	description="Command-line client for working with Velociraptor",
	long_description=long_description,
	author="Jason R. Coombs",
	author_email="jaraco@jaraco.com",
	url="https://bitbucket.org/yougov/vr.cli",
	packages=setuptools.find_packages(),
	namespace_packages=['vr'],
	zip_safe=False,
	classifiers = [
		"Development Status :: 5 - Production/Stable",
		"Intended Audience :: System Administrators",
		"Programming Language :: Python :: 2.7",
		"Programming Language :: Python :: 3",
	],
	entry_points=dict(
		console_scripts=[
			'vr.cli = vr.cli:handle_command_line',
		],
	),
	install_requires=[
		'jaraco.util>=8.5,<11dev',
		'vr.common>=3.7.1',
		'more_itertools',
	],
	setup_requires=[
		'hgtools',
	],
)
if __name__ == '__main__':
	setuptools.setup(**setup_params)
