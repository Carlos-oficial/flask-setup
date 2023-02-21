from setuptools import setup

setup(
    name="flask-setup",
    version="0.1.0",
    description="A package to facilitate the process of creating a flask web application",
    url="https://github.com/carlos-oficial/flask-setup",
    author="Carlos Ribeiro",
    author_email="carlosribeiro2003oficial@gmail.com",
    license="BSD 2-clause",
    packages=["flask_setup"],
    install_requires=[
        "flask>=2.2.2",
    ],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Python developers",
        "License :: MIT License",
        "Operating System :: Linux",
        "Programming Language :: Python :: 3.10",
    ]
)
