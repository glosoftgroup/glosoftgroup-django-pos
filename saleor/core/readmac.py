import sys
import os
import netifaces
from uuid import getnode as get_mac
import subprocess,time,socket
import base64

class FetchMac():

    def __init__(self):
        pass

    def getnumber_mac(self):
        ''' get mac as int form then converts back to hex form'''

        mac = "00:00:00:00:00:00"
        if sys.platform == 'win32':
            for line in os.popen("ipconfig /all"):
                if line.lstrip().startswith('Physical Address'):
                    mac = line.split(':')[1].strip().replace('-',':')
                    break
        if sys.platform == 'darwin':
            for line in os.popen("/sbin/ifconfig"):
                if line.find('ether') > -1:
                    mac = line.split()[-1]
                    break
        else:
            inf = netifaces.interfaces()
            for line in os.popen("/sbin/ifconfig"):
                for i in inf:
                    if i.startswith('en'):
                        if line.find(i) > -1:
                            mac = line.split()[4]
                            break

        return mac

    def format_machine(self, new_id):
        formatted = str(new_id)
        bb = base64.b64encode(bytes(formatted))
        bkey322 = bb.ljust(32)[:32]
        return bkey322

    def getnumber(self):
        mac = get_mac()
        h = iter(hex(mac)[2:].zfill(12))
        mac_addr = ":".join(i + next(h) for i in h)
        print("macadd : "+ mac_addr)
        if sys.platform == 'win32':
            mac_addr = self.windows()
            return mac_addr
        elif sys.platform == 'darwin':
            mac_addr = self.mac()
            return mac_addr
        else:
            mac_addr = self.unix()
            return mac_addr

    def windows(self):
        machine_id = subprocess.check_output('wmic csproduct get UUID').split('\n')[1].strip()
        machine_model_number = subprocess.check_output('wmic csproduct get IdentifyingNumber').split('\n')[1].strip()
        new_id = '{0}@/{1}*'.format(machine_id, machine_model_number)
        mid = self.format_machine(new_id)
        return mid

    def unix(self):
        machine_id = subprocess.check_output("dmesg | grep Kernel | sed s/.*UUID=//g | sed s/\ ro\ quiet.*//g", shell=True)
        new_id = '{0}'.format(machine_id)
        mid = self.format_machine(new_id)
        return mid


    def mac(self):
        machine_id = subprocess.check_output("ioreg -rd1 -c IOPlatformExpertDevice | grep -E '(UUID)'", shell=True)
        new_id = '*!%F{0}@*'.format(machine_id)
        mid = self.format_machine(new_id)
        return mid



