from setuptools import setup, find_packages
setup(
    name = "aaempire",
    version = "0.1",
    packages = find_packages(),
    scripts = ["aaempire.py"],
    install_requires = ["pygubu>=0.9.7"],
    package_data = {
        '':["*.ui"]
    },
    test_suite="tests",
    author = "Xulb Alien",
    author_email = "xulb.aa@gmail.com",
    description = "A simple GUI for controlling AlienArena servers",
    license = "GPLv2",
    keywords = "alienarena aa quake2 rcon",
    url = "https://github.com/xulb/aaserver"
)
