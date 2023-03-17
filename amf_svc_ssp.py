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
import time
import os

class ssp(amfservice):
    """
    IBM SSP
    This service controls SSP.
    """
    
    def __init__(self, svc, home):
        amfservice.__init__(self, svc, home)
        self.svc = svc
        self.home = home
        self.services = ['ssp', 'ssp2']
           
    def start(self):
        """start SSP"""
        status = 0
        for svchome in self.services:
            svchome = self.home + "/" + svchome
            self.printer.info("service at %s starting " % (svchome))
            status = self.run(svchome+"/bin/startEngine.sh >/dev/null 2>&1", noWait=True)
            if status:
                self.printer.error("service start failed")
            else:
                while True:
                    time.sleep(3)
                    status = self.run("ps -ef|grep -v grep|grep %s|grep SSPPlatformFactory|grep -c java" % (svchome), printflag=False)
                    val = self.outbuf[0]
                    if val > 0:
                        break
        return status 

    def stop(self):
        """stop SSP"""
        self.printer.info("service stopping")
        self.run(self.home+"/bin/stopEngine.sh mode=auto") 
        time.sleep(15)
        self.run("kill -9 `ps -ef|grep -v grep|grep SSPPlatformFactory|grep java|awk '{ print $2 }'` >/dev/null 2>&1; echo", printflag=False)

    def restart(self):
        """stops and starts SSP"""
        self.stop()
        status = self.start()
        return status
    
    def status(self):
        """reports status SSP"""
        self.printer.info("checking service status for engines:%s" % (self.services))
        status = 0
        found = False
        clist = []
        clist.append("%-20s%-12s%-10s" % ('PID FILE', 'PID', 'RUNNING'))
        clist.append('------------------------------------------')
        self.run("ps -ef | grep -v grep | grep SSPPlatformFactory| cut -c1-30", printflag=False)
        line = self.outbuf
        pid = 'unknown'
        proclist = []
        for line in self.outbuf:
            vals = line.split()
            if len(vals) > 1:
                #if vals[0] == 'admin':
                user = os.environ['USER']
                if vals[0] == user:
                    details = {}
                    details['pidfile'] = 'NA'
                    details['pid'] = vals[1]
                    details['status'] = True
                    found = True
                    pid = vals[1]
                    proclist.append(details)
                    if len(proclist) == len(self.services):
                        break
        self.printer.info(clist)
        status = 0
        message = ""
        for item in proclist:
            self.printer.info(["%-20s%-12s%-10s" % (item['pidfile'], item['pid'], item['status'])])
            #clist.append("%-20s%-12s%-10s" % ('NA', pid, found))
            if item['status'] and status == 0:
                message = "SSP is running"
            else:
                message = "SSP(s) is not running"
                status = 1
        if len(proclist) == 0:
            message = "SSP is not running"
            status = 1
        self.printer.info([message])
        return status
