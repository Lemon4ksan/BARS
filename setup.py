from setuptools import find_packages, setup

setup(
    name='BARS',
    version='1.1',
    description='BARS Rest-API',  # Добавьте описание
    packages=find_packages(),
    install_requires=[
        'httpx',
        'python-telegram-bot',
        'python-dotenv',
        'coloredlogs',
        'beautifulsoup4',
        'lxml'
    ],
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.12',
)
