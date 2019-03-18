from setuptools import setup

setup(
    name="app",
    packages=["app"],
    install_requires=["pytz"],
    setup_requires=["pytest-runner"],
    tests_require=["pytest", "pytest_mockito"],
)

