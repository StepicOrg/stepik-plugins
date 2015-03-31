import os

from setuptools import find_packages, setup


README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))
version = __import__('stepic_plugins').get_version()

setup(
    name='stepic-plugins',
    version=version,
    packages=find_packages(include=['stepic_plugins*']),
    include_package_data=True,
    author='Stepic Team',
    description='A collection of plugins for Stepic',
    long_description=README,
    url='https://stepic.org',
    install_requires=[
        'oslo.messaging==1.9.0',
    ],
    data_files=[
        ('stepic_plugins_data', ['Makefile']),
        ('stepic_plugins_data/requirements', ['requirements/sandbox_minimal.txt']),
    ],
)
