import sys

from setuptools import setup

meta = dict(
    name="sartoris",
    version="0.0.1",
    description="Tool to manage using git as a deployment management tool",
    author="Wikimedia Foundation",
    author_email="info@wikimedia.org",
    py_modules=["script"],
    test_suite="tests",
    install_requires=["setuptools"],
    keywords="scripts",
    url="http://packages.python.org/sartoris",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Topic :: Software Development :: Testing",
    ],
)

# Automatic conversion for Python 3 requires distribute.
if False and sys.version_info >= (3,):
    meta.update(dict(
        use_2to3=True,
    ))

setup(**meta)
