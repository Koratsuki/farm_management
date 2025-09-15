from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in farm_management/__init__.py
from farm_management import __version__ as version

setup(
	name="farm_management",
	version=version,
	description="Comprehensive Farm Management App for ERPNext - Poultry and Pig Farming Operations",
	author="Koratsuki",
	author_email="koratsuki.nijuusan@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
