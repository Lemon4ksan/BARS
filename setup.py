from setuptools import find_packages, setup

setup(
    name='BARS',
    version='1.1',
    author='Lemon4ksan (Bananchiki)',
    packages=find_packages(),
    install_requires=['httpx', 'python-telegram-bot', 'python-dotenv', 'coloredlogs', 'beautifulsoup4', 'lxml'],
    include_package_data=True,
)
