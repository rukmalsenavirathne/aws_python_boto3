import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="boto3form",
    version="0.0.1",
    author="Rukmal Senavirathne",
    description="Create and delete aws ecr repository using python boto3 like terraform ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # packages=setuptools.find_packages(),
    packages=setuptools.find_packages(),
    # package_dir={"": "boto3form"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=['boto3'],
    url="https://github.com/rukmalsenavirathne/aws_python_boto3"
)