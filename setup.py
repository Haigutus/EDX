from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='EDX',
    version='0.0.7',
    packages=['EDX'],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/Haigutus/EDX',
    license='GPL2',
    author='Kristjan Vilgo',
    author_email='kristjan.vilgo@gmail.com',
    description='EDX SOAP API implementation in python',
    install_requires=[
        "requests", "zeep", 'urllib3'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
    ]
)
