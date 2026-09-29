#!/usr/bin/env python3
from setuptools import setup

setup(
    name="wtime",
    version="0.1.0",
    description="INFN working-time tracker: report, GUI and portal autoclocking",
    author="Riccardo Bruno",
    author_email="riccardo.bruno@gmail.com",
    license="Apache",
    py_modules=[
        "wtimecore",
        "wtimegui",
        "wtimecli",
        "portal_session",
        "autoclocking",
        "autoclocking_data",
    ],
    entry_points={
        "console_scripts": [
            "wtime=wtimecli:main",
        ],
    },
    install_requires=[
        "selenium",
    ],
    python_requires=">=3.7",
)
