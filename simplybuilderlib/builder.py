import subprocess
import os
import shutil
import deb822

class SBBuilder():
    

    def __init__(self,config, chroot):
       self.config = config
       self.chroot = chroot

    def prepare(self):
        
        ccache_path = self.config.get('simply-buildpackage','ccache-path')
        
        path = os.getenv('PATH')
        if path and ccache_path != '':
            os.putenv('PATH','/usr/lib/ccache:%s' % path)
            os.putenv('CCACHE_DIR', ccache_path)
            os.putenv('CCACHE_NLEVELS', '4')
            os.putenv('CCACHE_COMPILERCHECK' , 'content')
        os.putenv('LANG','C')
        os.putenv('LC_ALL','C')
        os.putenv('DEBIAN_FRONTEND','noninteractive')

        self.build_location = os.path.join(self.chroot.chroot_info['location'],"build")

        self.chroot.run(['mkdir' , '-v' , '-p', "/build" ])

    def copy_dsc_files(self):
        
        ok = False
        with open(self.config.dsc) as dsc_file:
            dsc_obj = deb822.Dsc(dsc_file)
            dsc_file.close()
          
            (path_head,path_tail) = os.path.split(self.config.dsc)

            print(path_head,path_tail)
         
            file_srcs = [self.config.dsc]
            for f in dsc_obj['Files']:
                file_srcs += [os.path.join(path_head,f['name'])]

            for f in file_srcs:
                print("I: Copying '%s' to '%s'"% (os.path.basename(f) , self.build_location) )
                shutil.copy2(os.path.join(path_head,f), self.build_location)

            ok = True

        return ok

    def build(self):
        ok = False
        dsc = os.path.splitext(os.path.basename(self.config.dsc))[0]

        cmd = ['dpkg-source' ,'-x' ,"%s.dsc" % dsc, dsc]
        self.chroot.run(cmd,x_dir='/build')
        #subprocess.Popen(cmd , cwd='/').wait()

        cmd = ['dpkg-buildpackage' ,'-b' , '-us' , '-uc']
        retcode = self.chroot.run(cmd,x_dir='/build/%s'%dsc)
        #retcode = subprocess.Popen(cmd , cwd='/').wait()

        if (retcode):
            print('E: dpkg-buildpackage failed to build (%s)' % retcode )
        else:
            ok = True

        return ok

    def copy_result(self):
        dsc = os.path.splitext(os.path.basename(self.config.dsc))[0]
        files = os.listdir( os.path.join(self.build_location,dsc) )
        for f in files:
            if os.path.isfile(f) and not os.path.islink(f):
                shutil.copy2(f, "/tmp/")
