# setup.py
from setuptools import setup, find_packages

setup(
    name="storyboard-generator",
    version="1.0.0",
    description="A simple desktop application for creating film storyboards",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "Pillow>=9.0.0",
        "reportlab>=3.6.0",
    ],
    entry_points={
        'console_scripts': [
            'storyboard-generator=storyboard_generator.main:main',
        ],
    },
    python_requires='>=3.7',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
