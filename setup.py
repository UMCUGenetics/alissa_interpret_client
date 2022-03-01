import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt") as requirements_file:
    requirements = requirements_file.readlines()

setuptools.setup(
    name="alissa_interpret_client",
    version="1.0.0",
    author="Robert Ernst",
    author_email="r.f.ernst-3@umcutrecht.nl",
    description="Alissa Interpret Public Api Client",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/UMCUGenetics/alissa_interpret_client",
    project_urls={
        "Bug Tracker": "https://github.com/UMCUGenetics/alissa_interpret_client/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    install_requires=requirements,
    entry_points={
        'console_scripts': ['alissa_client=alissa_interpret_client.cli:main'],
    }
)
