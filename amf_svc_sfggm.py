'''
##################################################################################
# License: MIT
# Copyright 2018 Agile Data Inc
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of 
# this software and associated documentation files (the "Software"), to deal in 
# the Software without restriction, including without limitation the # rights to 
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of 
# the Software, and to permit persons to whom the Software is furnished to do so, 
# subject to the following conditions:
# The above copyright notice and this permission notice shall be included in 
# all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A 
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE # AUTHORS OR COPYRIGHT 
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF 
# CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE 
# OR THE USE OR OTHER DEALINGS IN  # THE SOFTWARE.
##################################################################################
'''
from amf import amfservice
import os
import json
import time

class sfggm(amfservice):
    '''
    This service SFG-GM
    '''

    def __init__(self, svc, home):
        amfservice.__init__(self, svc, home)
        self.svc = svc
        self.home = home
    

    def start(self):
        self.suppress_output = True
        status = 0
        is_alive = self.status()
        if is_alive != 0:
            self.printer.info('SFG-GM service are starting')   
            if self.run(self.home+'/MailboxUtilities/bin/startGM.sh', printflag=False):
                if str(self.outbuf).find('Server mailboxui stopped.') != -1:
                    print("SFG-GM started")
                else:
                    print('SFG-GM failed to start')
                    status = 1
            if status:
                print('Failed to start SFG-GM service')
            else:
                print('SFG-GM service started successfully')
        else:
            self.printer.info('SFG-GM service already running')
        return status

    def stop(self):
        status = 0
        self.printer.info('SFG-GM service are stopping')   
        if self.run(self.home+'/MailboxUtilities/bin/stopGM.sh', printflag=False):
            if str(self.outbuf).find('Server mailboxui started with process ID') != -1:
                print("SFG-GM stopped")
            else:
                print('Failed to stop SFG-GM')
                status = 1
        if status:
            print('Failed to stop SFG-GM  service')
        else:
            print('SFG-GM service stopped successfully')
        return status


    def restart(self):
        self.stop()
        time.sleep(10)
        self.start()


    def status(self):
        """reports status of all SFG-GM"""
        status = 0
        count = 0
        clist = []
        clist.append('%-50s%-12s%-10s' % ('PID FILE', 'PID', 'RUNNING'))
        clist.append('---------------------------------------------------------')
        self.run('ps -ef | grep java | cut -c1-30', printflag=False)
        pidfiles = []
        if 'GlobalMailbox' in os.environ:
            self.run("ps -ef | grep mailboxui | grep -v grep | awk '{print $2}'",printflag=True) 
            mailboxui_pid = str(self.outbuf).replace('[','').replace("'","").replace(']','')
            if mailboxui_pid != "":
                clist.append('%-50s%-12s%-10s' % ("SFG-GM", mailboxui_pid , True))
            else:
                self.printer.info('SFG-GM is not running')
                status = 1
        self.printer.info(clist)
        if status == 0:
            self.printer.info("SFG-GM services are up")
        else:
            self.printer.info("SFG-GM services are down")
        return status
