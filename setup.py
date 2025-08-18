"""
Setup script for pico-report package.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pico-report",
    version="1.0.0",
    author="Pico Team",
    author_email="team@picolm.io",
    description="A Python package for uploading training metrics and checkpointing data to Pico backend databases",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/picolm/pico-report",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.10,<3.13",
    install_requires=[
        "requests>=2.31.0",
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
        "click>=8.1.7",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-mock>=3.11.1",
            "black>=23.7.0",
            "isort>=5.12.0",
            "mypy>=1.5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "pico-report=pico_report.cli:main",
        ],
    },
)