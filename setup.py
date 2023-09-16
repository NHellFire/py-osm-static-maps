#!/usr/bin/env python3
import glob
from setuptools import setup, find_packages

requires=[
    "selenium",
    "flask",
    "Pillow"
]

setup(
    name="osm-static-maps",
    version="1.0.0",
    packages=find_packages(include=["*"]),
    license_files=["LICENSE"],
    license="GPL-2",
    entry_points={
        "console_scripts": [ "osmsm=osm_static_maps.main:main" ]
    },
    package_data={
        "osm_static_maps": [ "static/*", "static/images/*", "templates/*" ]
    },
    requires=requires,
    install_requires=requires
)
