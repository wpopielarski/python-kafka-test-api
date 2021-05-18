from setuptools import setup, find_packages

from setup_utils import CleanCommand, LintCommand, TypecheckCommand

setup(
    name="bpf",
    # update version if needed
    version="1.0.0-SNAPSHOT",
    packages=find_packages(exclude=["tests"]),
    setup_requires=["pytest-runner", "pyspark"],
    # add dependent module name(s) if needed
    # install_requires=["pyspark"],
    # tests_require=["pytest", "pandas"],
    # add/change tests requirements if needed
    author="Wieslaw Popielarski",
    author_email="wieslaw.popielarki@tesco.com",
    description="Forecasts promotions plans and results.",
    cmdclass={
        'clean': CleanCommand,
        'lint': LintCommand,
        'typecheck': TypecheckCommand
    }
)
