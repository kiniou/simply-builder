import subprocess



class SBChroot():

    config = None
    session = None

    def __init__(self,config):
        self.config = config

        self.chroot_info = {
            "name" : "chroot:%s-%s-sbuild" % (config.release,config.arch),
            "session": None,
            "location": None,
        }


    def begin_session(self,x_session=None):
        
        #TODO: use an existing session if provided
        #if (x_session is not None):
            
        #check if chroot exists
        cmd = ['schroot' , '-c', '%s' % self.chroot_info['name'], '--list']
        chroot_not_found = subprocess.Popen(cmd,cwd='/').wait()
        if chroot_not_found:
            print("E: chroot %s doesn't exist!!" % self.chroot_info['name'])
            exit()

        cmd = [ 'schroot' , '--begin-session' , '-c' , self.chroot_info['name']]
        p = subprocess.Popen(cmd,cwd='/',stdout=subprocess.PIPE)
        (r_stdout,r_stderr)=p.communicate()
        self.chroot_info['session'] = r_stdout.strip()

        self.schroot_cmd = ['schroot' , '-c' , 'session:%s' % ( self.chroot_info['session'] ) ]

        cmd = self.schroot_cmd + [ '--location' ]
        
        p = subprocess.Popen(cmd,cwd='/',stdout=subprocess.PIPE)
        (r_stdout,r_stderr)=p.communicate()
        self.chroot_info['location'] = r_stdout.strip()

        print("I: Starting Chroot %s"  % self.chroot_info['name'] )
        print("I:   * Session : %s"    % self.chroot_info['session'] )
        print("I:   * Location: %s"    % self.chroot_info['location'] )

    def end_session(self):
        
        cmd = self.schroot_cmd + [ '--end-session' ]
        subprocess.Popen(cmd,cwd='/').wait()


    def run(self, x_cmd, x_shell=False, x_user=None, x_dir=None):
        cmd = []
        cmd += self.schroot_cmd

        if x_user:
            cmd += [ '-u', x_user ]

        if x_dir:
            cmd += [ '-d', x_dir ]

        cmd += ['--run-session', '--']
        cmd += x_cmd

        print("D: execute '%s'" % " ".join(cmd))
        if x_shell: cmd = " ".join(cmd)

        return( subprocess.Popen(cmd , cwd='/',shell=x_shell).wait() )
        
