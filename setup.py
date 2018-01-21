#!/usr/bin/env python

import setuptools

readme = open('README.md').read()
requirements = open("requirements.txt").readlines()

setuptools.setup(
    name = 'mqttStat',
    version = '1.0',
    description = "RCS Thermostat <-> MQTT bridge",
    long_description = readme,
    author = "Ben Franske",
    author_email = '',
    url = 'https://github.com/bfranske/mqttStat',
    packages = setuptools.find_packages(),
    scripts = ['scripts/mqttStat','scripts/getStat','scripts/setStat','scripts/schedStat'],
    include_package_data = True,
    install_requires = requirements,
    license = "GNU General Public License v3",
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
    ],
    # avoid eggs
    zip_safe = False,
)
