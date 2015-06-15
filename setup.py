import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

LONG_DESC = open(os.path.join(os.path.dirname(__file__), "README.md")).read()
with open(os.path.join(os.path.dirname(__file__), "requirements.txt")) as f:
    requires = f.read().splitlines()

setup(
    name="salinity",
    version="0.1",
    description="Test salt states on a local docker environment",
    long_description=LONG_DESC,
    author="Julien Seiler",
    author_email="julien.seiler@gmail.com",
    license="GNU GENERAL PUBLIC LICENSE v2",
    url="http://github.com/julozi/salinity",
    zip_safe=False,
    install_requires=requires,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        'Natural Language :: English',
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
    ],

    scripts=['salinity']
)
