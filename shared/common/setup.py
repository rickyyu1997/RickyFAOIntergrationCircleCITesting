from setuptools import setup, find_packages

setup(
    name='newstore_common',
    author="NewStore Inc.",
    author_email='dev@newstore.com',
    version='1.0.0',
    packages=find_packages(),
    data_files=[],
    include_package_data=True,
    python_requires='>=3.6',
    # install_requires=['newstore_adapter']
)
