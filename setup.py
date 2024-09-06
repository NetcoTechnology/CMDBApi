from setuptools import setup, find_packages

setup(
    name='CMDBApiWrapper',
    version='0.1.0',
    author='Jelle Stoel',
    author_email='',
    packages=find_packages(),
    url='https://github.com/NetcoTechnology/CMDBApiWrapper',
    license='LICENSE.txt',
    description='An API wrapper library for interacting with the CMDB API.',
    long_description=open('README.md').read(),
    install_requires=[
        "requests >= 2.31.0"
    ],
    extras_require={
        'dev': [
            "python-dotenv >= 1.0.0"
        ]
    }
)

