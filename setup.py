# -*- coding: utf-8 -*-

"""Distutils setup.py."""

from setuptools import setup, find_packages

from may4_challenge import __version__

setup(
    name='may4_challenge',
    version=__version__,
    description='Happy birthday IQX!',
    long_description='Validation API for May, the 4th, Challenge.',
    url='https://quantum-computing.ibm.com/',
    author='IBM Quantum Community Team',
    author_email='salvador.de.la.puente.gonzalez@ibm.com',
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.7",
        "Topic :: Scientific/Engineering",
    ],
    keywords="iqx quantum flask challenge may 4th anniversary birthday",
    packages=find_packages(include=[
        'may4_challenge',
        'may4_challenge.*',
        'may4_challenge_common',
        'may4_challenge_common.*'
    ]),
    install_requires=[
        'seaborn',
        'requests',
        'qiskit-terra>=0.13,<0.14',
        'qiskit-aer>=0.5,<0.6',
        'numpy',
        'ipython',
        'ipywidgets',
        'matplotlib'
    ],
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.7",
)
