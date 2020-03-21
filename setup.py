import setuptools
import os
import sys
from setuptools.command.install import install

VERSION = "0.1.0"

with open("README.md", "r") as fh:
    long_description = fh.read()


class VerifyVersionCommand(install):
    """Custom command to verify that the git tag matches our version"""
    description = 'verify that the git tag matches our version'

    def run(self):
        tag = os.getenv('CIRCLE_TAG')

        if tag == None:
            info = "No new version to upload"
            print(info)
        elif tag != VERSION:
            info = "Git tag: {0} does not match the version of this app: {1}".format(
                tag, VERSION
            )
            sys.exit(info)


setuptools.setup(
    name="ausbills",  # Replace with your own username
    version=VERSION,
    author="Kipling Crossing",
    author_email="kip.crossing@gmail.com",
    description="Get parliament bills for Australian governments.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/KipCrossing/Aus-Bills-Discord-Bot",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    cmdclass={
        'verify': VerifyVersionCommand,
    }
)
