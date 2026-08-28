from setuptools import setup, find_packages

setup(
    name="afrojobspy",
    version="1.0.0",
    license="MIT",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0",
        "pydantic>=2.0.0",
        "pandas>=2.0.0",
    ],
)
