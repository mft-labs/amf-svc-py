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

class cass(amfservice):
    '''
    This service Cassandra
    '''
    pidfiles = ['/apache-cassandra/bin/cassandra.pid']
           
    def __init__(self, svc, home):
        amfservice.__init__(self, svc, home)
        self.svc = svc
        self.home = home


    def start(self):
        is_alive = self.status()
        status = 0
        if is_alive != 0:
            self.suppress_output = True
            self.printer.info('Cassandra service are starting')   
            if self.run(self.home+'/MailboxUtilities/bin/startGMData.sh', printflag=False):
                if str(self.outbuf).find('Starting Cassandra ... STARTED') != -1:
                    print("Casssandra started")
                else:
                    print('Cassandra failed to start')
                    status = 1
            if status:
                print('Failed to start Cassandra service')
            else:
                print('Cassandra service started successfully')
        else:
            self.printer.info('Cassandra service already running')
        return status

    def stop(self):
        status = 0
        self.printer.info('Cassandra service are stopping')   
        if self.run(self.home+'/MailboxUtilities/bin/stopGMData.sh', printflag=False):
            if str(self.outbuf).find('Stopping Cassandra ... ... STOPPED') != -1:
                print("Cassandra stopped")
            else:
                print('Failed to stop Cassandra')
                status = 1
        if status:
            print('Failed to stop Cassandra service')
        else:
            print('Cassandra service stopped successfully')
        return status


    def restart(self):
        self.stop()
        time.sleep(10)
        self.start()


    def status(self):
        """reports status of all Cassandra"""
        self.printer.info("Checking service status")
        status = 0
        count = 0
        clist = []
        clist.append("%-65s%-12s%-10s" % ('PID FILE', 'PID', 'RUNNING'))
        clist.append('------------------------------------------------------------------------------------')
        self.run("ps -ef | grep java | cut -c1-30", printflag=False)
        for fname in self.pidfiles:
            found = False
            pid = ''
            filename = ""
            if os.path.exists(self.home+fname):
                filename = self.home+fname
            elif os.path.isfile(fname):
                filename = fname

            if os.path.exists(filename):
                count += 1
                f = open(filename)
                pid = f.read().strip()
                f.close()
                for line in self.outbuf:
                    vals = line.split()
                    if vals[1] == pid:
                        found = True
                        break
            
            clist.append("%-65s%-12s%-10s" % (self.home+fname, pid, found))
            if not found:
                status = 1 
        if count == 0: status = 1
        self.printer.info(clist)
        if status == 0:
            self.printer.info("Cassandra service are up")
        else:
            self.printer.info("Cassandra service are down")
        return status


