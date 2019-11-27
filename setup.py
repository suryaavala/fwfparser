from setuptools import setup, find_packages

version = open("VERSION").read().strip()
license = open("LICENSE").read().strip()

setup(
    name="fwfparser",
    version=version,
    license=license,
    author="Surya Avala",
    author_email="suryaavala.eliiza.com.au",
    url="https://github.com/suryaavala/fixedwidthfiles",
    description="Parse Fixed width files, convert them to delimited (csv's)",
    long_description=open("README.md").read().strip(),
    packages=find_packages(),
    install_requires=[
        # just python standard library
    ],
    test_suite="tests",
    entry_points={"console_scripts": ["fwfparser = fwfparser.__main__:main"]},
)
