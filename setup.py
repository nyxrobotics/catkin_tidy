from setuptools import setup, find_packages

setup(
    name="catkin_tidy",
    version='0.0.0',
    packages=find_packages(),
    entry_points={
        'catkin_tools.commands.catkin.verbs': [
            'clang_tidy = clang_tidy.tidy:description',
            'clang_build = clang_build.build:description',
            ],
        },
    )
