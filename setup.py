import os
import setuptools

base_dir = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(base_dir, "README.md"), 'r') as f:
    long_description = f.read()

setuptools.setup(
    name="fdsdecompose",
    author="FZJ IAS-7/BUW CCE (Prof. Dr. Lukas Arnold, Jan Vogelsang)",
    author_email="l.arnold@fz-juelich.de",
    description="Python script to automate decomposition of MESH statements.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/FireDynamics/FDSMeshDecomposer",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[],
    entry_points={
        'console_scripts': [
            'fdsdecompose = fdsdecompose.main:main',
        ],
    },
    version="1.0.2"
)
