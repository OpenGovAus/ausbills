import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ausbills", # Replace with your own username
    version="0.0.1",
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
)
