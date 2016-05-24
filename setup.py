#!/usr/bin/env python
# Generated by jaraco.develop 2.27.1
# https://pypi.python.org/pypi/jaraco.develop

import io
import sys

import setuptools

with io.open('README.rst', encoding='utf-8') as readme:
    long_description = readme.read()

needs_pytest = {'pytest', 'test'}.intersection(sys.argv)
pytest_runner = ['pytest_runner'] if needs_pytest else []
needs_sphinx = {'release', 'build_sphinx', 'upload_docs'}.intersection(sys.argv)
sphinx = ['sphinx'] if needs_sphinx else []
needs_wheel = {'release', 'bdist_wheel'}.intersection(sys.argv)
wheel = ['wheel'] if needs_wheel else []

setup_params = dict(
    name='vr.cli',
    use_scm_version=True,
    author="Jason R. Coombs",
    author_email="jaraco@jaraco.com",
    description="Command-line client for Velociraptor",
    long_description=long_description,
    url="https://bitbecket.org/yougov/vr.cli",
    packages=setuptools.find_packages(),
    include_package_data=True,
    namespace_packages=['vr'],
    install_requires=[
        'jaraco.functools>=1.0,<2dev',
        'vr.common>=4.6',
        'more_itertools',
        'six',
        'datadiff>=1.1.6',
        'jaraco.ui>=1.2',
        'jaraco.timing',
        'jaraco.logging',
    ],
    extras_require={
    },
    setup_requires=[
        'setuptools_scm>=1.9',
    ] + pytest_runner + sphinx + wheel,
    tests_require=[
        'pytest>=2.8',
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
    ],
    entry_points={
        'console_scripts': [
            'vr.cli = vr.cli:handle_command_line',
        ],
    },
)
if __name__ == '__main__':
    setuptools.setup(**setup_params)
