import electrum_scripting, os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='electrum_scripting',
    version=electrum_scripting.__VERSION__,
    description="Electrum wallet scripting interface wrapper",
    long_description=long_description,
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Topic :: Internet :: Crypto :: Wallet',
        'Programming Language :: Python :: 3',
        'Environment :: Linux Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
    ],
    keywords='Electrum Scripting Wallet Bitcoin Crypto',
    author="Stefan Liu",
    author_email="stefanliu@outlook.com",
    url="http://github.com/devfans/electrum-scripting",
    license="MIT",
    packages=["electrum_scripting"],
    include_package_data=True,
    zip_safe=True
)
