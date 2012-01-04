import os
import subprocess
import deb822
from string import Template


class SBResolver():
    
    satisfydepends_control = """
Package: pbuilder-satisfydepends-dummy
Version: 0.invalid.0
Architecture: $ARCH
Maintainer: Debian Pbuilder Team <pbuilder-maint@lists.alioth.debian.org>
Description: Dummy package to satisfy dependencies with aptitude - created by pbuilder
 This package was created automatically by pbuilder to satisfy the
 build-dependencies of the package being currently built.
$DEPENDS$CONFLICTS"""
    satisfydepends_pkgname = "pbuilder-satisfydepends-dummy"

    def __init__(self,config,chroot):
        self.config = config
        self.chroot = chroot
        self.generate_satisfydepends()

    def generate_satisfydepends(self):

        dsc_file = file(self.config.dsc)
        dsc = deb822.Dsc(dsc_file)
        dsc_file.close()

        if(dsc.has_key('Build-Depends') ):
            depends = dsc['Build-Depends']
        else:
            depends = None
        if( dsc.has_key('Build-Conflicts') ):
            conflicts = dsc['Build-Conflicts']
        else:
            conflicts = None


        s = Template(self.satisfydepends_control)
        v = {}
        v['ARCH'] = self.config.arch
        if depends :
            v['DEPENDS']= "Depends: %s\n" % depends
        else:
            v['DEPENDS'] = ""
        if conflicts : 
            v['CONFLICTS'] = "Conflicts: %s\n" % conflicts
        else:
            v['CONFLICTS'] = ""

        self.satisfydepends_control = s.safe_substitute(v)

    def install_satisfydepends(self):
        
        build_dep_pkg_name = "pbuilder-satisfydepends-dummy"
        build_dep_deb_dir = os.path.join("/tmp/satisfydepends-aptitude",build_dep_pkg_name)
        #control_file = generate_dummy_pkg(args.arch , args.release, args.file )

        
        cmd = ['mkdir' , '-v' , '-p', os.path.join(build_dep_deb_dir,"DEBIAN")]
        self.chroot.run(cmd)
        #subprocess.Popen(cmd,cwd='/').wait()

        cmd = ['sh', '-c', '"cat >%s"' % os.path.join(build_dep_deb_dir,"DEBIAN","control"),'<<',''.join(['EOF',self.satisfydepends_control,'EOF'])]
        self.chroot.run(cmd,x_shell=True)
        #subprocess.Popen(" ".join(cmd),shell=True,cwd='/').wait()
        
        cmd = ['cat' , os.path.join(build_dep_deb_dir,"DEBIAN","control")]
        self.chroot.run(cmd)
        #subprocess.Popen(cmd,cwd='/').wait()
       
        cmd = ['dpkg-deb', '-b', build_dep_deb_dir] 
        self.chroot.run(cmd)
        #subprocess.Popen(cmd,cwd='/').wait()

        cmd = [ 'dpkg', '-i', "%s.deb" % build_dep_deb_dir] 
        self.chroot.run(cmd,x_user='root')
        #subprocess.Popen(cmd,cwd='/').wait()

        cmd = [   
            'aptitude', 
            '-y', 
            '--without-recommends',
            '-o', 'APT::Install-Recommends=false',
            '-o', 'Aptitude::ProblemResolver::StepScore=100',
            'install',
            build_dep_pkg_name
        ] 
        self.chroot.run(cmd,x_user='root')
        #subprocess.Popen(cmd,cwd='/').wait()
        
        cmd = ['dpkg', '-l', 'pbuilder-satisfydepends-dummy', '2>/dev/null' ]
        self.chroot.run(cmd,x_shell=True)
        #subprocess.Popen(cmd,shell=True,cwd='/').wait()
        cmd = ['dpkg', '-l', 'pbuilder-satisfydepends-dummy', '2>/dev/null', '|', 'grep', '-q', '^ii' ]
        retcode = self.chroot.run(cmd,x_shell=True)
        #retcode = subprocess.Popen(cmd,shell=True,cwd='/').wait() 
        print("RETURNCODE %d" % retcode)

