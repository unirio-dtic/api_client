# coding=utf-8
from setuptools import setup, find_packages
from os import path

VERSION = '1.1.1'

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst')) as f:
    README = f.read()

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='unirio-api',
    version=VERSION,
    packages=find_packages(exclude=['*test*']),
    description='Client package for the RESTful api provided by the Universidade '
                'Federal do Estado do Rio de Janeiro (UNIRIO)',
    long_description=README,
    url='https://github.com/unirio-dtic/api_client',
    author='Diogo Magalhães Martins',
    author_email='magalhaesmartins@icloud.com',
    license='GPLv2',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'License :: Public Domain',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    keywords='unirio api rest sie development',
    install_requires=required
)

# todo: pre-publish -> pandoc --from=markdown --to=rst --output=README.rst README.md
