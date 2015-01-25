import ez.ez_setup
ez.ez_setup.use_setuptools()
import sys
import os.path
from setuptools import setup, find_packages
from pkg_resources import resource_string,resource_filename

if (sys.version_info[0] < 3):
    print("Sorry, Python 3 is required.")
    sys.exit(1)
try: 
    dum = resource_string('tests','testArgs.py')
except FileNotFoundError:
    loc = resource_filename('tests','')
    print("Enter server info for tests:")
    try:
        host = input("Test server host [ENTER to skip this]: ")
        if (not host):
            raise BaseException
        port = input("Test server port: ")
        pw = input("Test server rcon_pass: ")
        argf = open(os.path.join(loc,'testArgs.py'), mode="w")
        print ("""
class testArgs:
    def __init__(self):
        self.host = \'{host}\'
        self.port = {port}
        self.passwd = \'{pw}\'
            """.format(host=host,port=port,pw=pw),file=argf)
        argf.close()
    except:
        pass

setup(
    name = "aaempire",
    version = "0.1",
    packages = ["ez","empire","empire.view","empire.controller","empire.model"],
    scripts = ["aaempire"],
    install_requires = ["pygubu>=0.9.7"],
    package_data = {
        'empire.view':["*.ui"],
    },
    test_suite="tests",
    author = "Xulb Alien",
    author_email = "xulb.aa@gmail.com",
    description = "A simple GUI for controlling AlienArena servers",
    license = "GPLv2",
    keywords = "alienarena aa quake2 rcon",
    url = "https://github.com/xulb/aaserver"
)
