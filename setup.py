import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sqlite-tables-joshu",
    version="0.0.1",
    author="Joshua Munn",
    author_email="joshamunn@gmail.com",
    description="Classes for sqlite3 interaction",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jams2/sqlite-tables",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
