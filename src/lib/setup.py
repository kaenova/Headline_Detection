import setuptools

setuptools.setup(
    name = "kaelib",
    version = "0.0.1",
    author = "Kaenova Mahendra Auditama",
    author_email = "kaenova@gmail.com",
    description = "A most used private, hand made library by Kaenova ;)",
    classifiers = [
        "Programming Language :: Python :: 3",
    ],
    package_dir = {"": "src"},
    packages = setuptools.find_packages(where="src"),
    python_requires = ">=3.9"
)