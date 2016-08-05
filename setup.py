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
    if sys.version_info[:2] < (3, 5):
        return ["typing>=3.5.2"]
    return []


setup(
    name='python-interface',
    version='1.0.0',
    description="Pythonic Interface definitions",
    author="Scott Sanderson",
    author_email="scott.b.sanderson90@gmail.com",
    packages=find_packages(),
    long_description=long_description,
    license='Apache 2.0',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Pre-processors',
    ],
    url='https://github.com/ssanderson/interface',
    install_requires=install_requires(),
    extras_require=extras_require(),
)
