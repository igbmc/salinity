import os

from pip.req import parse_requirements

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

LONG_DESC = open(os.path.join(os.path.dirname(__file__), "README.md")).read()
install_reqs = parse_requirements(os.path.join(os.path.dirname(__file__), "requirements.txt"))
reqs = [str(ir.req) for ir in install_reqs]

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
    install_requires=reqs,
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
