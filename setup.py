from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="fcb1010-editor",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A Python library for interfacing with the Behringer FCB1010 MIDI foot controller",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/fcb1010-editor",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Topic :: Multimedia :: Sound/Audio :: MIDI",
    ],
    python_requires=">=3.6",
    install_requires=[
        "rtmidi",
        "gspread",
        "oauth2client",
    ],
)
