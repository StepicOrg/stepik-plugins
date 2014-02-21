import os

from setuptools import setup, find_packages


README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))
version = __import__('stepic_plugins').get_version()

setup(
    name='stepic-plugins',
    version=version,
    packages=find_packages(),
    include_package_data=True,
    author='Stepic Team',
    description='A collection of plugins for Stepic',
    long_description=README,
    url='https://stepic.org',
)
