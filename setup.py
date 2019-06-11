from setuptools import setup, find_packages

setup(
    name="sheetscrape",
    version="0.0.0",
    author="Davis Bennett",
    packages=find_packages(exclude=["*.pyc"]),
    include_package_data=True,
    install_requires=["oauth2client", "gspread", "Pandas"]
    )
