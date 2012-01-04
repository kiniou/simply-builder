from ConfigParser import SafeConfigParser
from pprint import pprint

from StringIO import StringIO
import os
import collections

class SBConfig(SafeConfigParser):
    
    defaults = {

        "simply-createchroot": {
        },

        "simply-buildpackage": {
                "lintian-use" : "True",
                "lintian-opts" : "-Ivi --pedantic",
                "ccache-use" : "False",
                "ccache-path" : "",
                "build-result" : "",
        },
    }

    arch = None
    release = None
    dsc = None

    config_files = [os.path.expanduser('~/.simply-builder/main.cfg')]

    def __init__(self,arch,release,dsc):

        self.arch = arch
        self.release = release
        self.dsc = dsc

        SafeConfigParser.__init__(self)


        for s in self.defaults:
            print("Section '%s'" % s)
            self.add_section(s)
            for o,v in self.defaults[s].items():
                print(" %s = %s" % (o,v))
                self.set(s,o,v)

        self.read(self.config_files)

        f = StringIO()
        self.write(f)
        print("Contents of config")
        print(f.getvalue())
        f.close()

