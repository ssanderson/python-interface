#!/usr/bin/env python
from setuptools import setup, find_packages
import sys

long_description = ''

if 'upload' in sys.argv:
    with open('README.rst') as f:
        long_description = f.read()


def extras_require():
    return {
        'test': [
            'tox>=2.0',
            'pytest>=2.8.5',
            'pytest-cov>=1.8.1',
            'pytest-pep8>=1.0.6',
        ],
    }


def install_requires():
    requires = ['six']
    if sys.version_info[:2] < (3, 5):
        requires.append("typing>=3.5.2")
    if sys.version_info[0] == 2:
        requires.append("funcsigs>=1.0.2")
    return requires


setup(
    name='python-interface',
    version='1.2.0',
    description="Pythonic Interface definitions",
    author="Scott Sanderson",
    author_email="scott.b.sanderson90@gmail.com",
    packages=find_packages(),
    long_description=long_description,
    license='Apache 2.0',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Pre-processors',
    ],
    url='https://github.com/ssanderson/interface',
    install_requires=install_requires(),
    extras_require=extras_require(),
)
