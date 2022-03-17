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

class zoo(amfservice):
    '''
    This service Zookeeper
    '''
    pidfiles = []
           
    def __init__(self, svc, home):
        amfservice.__init__(self, svc, home)
        amfservice.__init__(self, svc, home)
        val = os.getenv('USE_ZOOKEEPER')
        self.zookeeper_exists = False
        if val and val.lower() == "true":
            self.zookeeper_exists = True
            zmap = self.get_zookeeper_properties()
            if 'dataDir' in zmap:
                dataDir  = zmap['dataDir']
                self.pidfiles.extend([dataDir+'/zookeeper_server.pid'])
        self.svc = svc
        self.home = home

    def get_zookeeper_properties(self):
        pmap = {}
        pfile = os.environ["AMF_GM_HOME"]+"/zookeeper/conf/zoo.cfg"
        if os.path.isfile(pfile):
            d = open(pfile, 'r').read()
            for line in d.split('\n'):
                line = line.strip()
                if line.startswith("#"):
                    continue
                vals = line.split("=", 1)
                if len(vals) == 2:
                    key = vals[0].strip()
                    val = vals[1].strip()
                    pmap[key] = val
        return pmap

    def start(self):
        self.suppress_output = True
        status = 0
        is_alive = self.status()
        if is_alive != 0:
            self.printer.info('ZooKeeper service are starting')   
            if self.run(self.home+'/MailboxUtilities/bin/startGMCoordinate.sh', printflag=False):
                if str(self.outbuf).find('Starting ZooKeeper ... STARTED') != -1:
                    print("ZooKeeper started")
                else:
                    print('ZooKeeper failed to start')
                    status = 1
            if status:
                print('Failed to start ZooKeeper service')
            else:
                print('ZooKeeper service started successfully')
        else:
            self.printer.info('ZooKeeper service already running')
        return status

    def stop(self):
        status = 0
        self.printer.info('ZooKeeper service are stopping')   
        if self.run(self.home+'/MailboxUtilities/bin/stopGMCoordinate.sh', printflag=False):
            if str(self.outbuf).find('Stopping ZooKeeper ... ... STOPPED') != -1:
                print("ZooKeeper stopped")
            else:
                print('Failed to stop ZooKeeper')
                status = 1
        if status:
            print('Failed to stop ZooKeeper service')
        else:
            print('ZooKeeper service stopped successfully')
        return status


    def restart(self):
        self.stop()
        time.sleep(10)
        self.start()


    def status(self):
        """reports statu of all ZooKeeper"""
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
            self.printer.info("ZooKeeper service are up")
        else:
            self.printer.info("ZooKeeper service are down")
        return status


