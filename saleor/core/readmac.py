import sys
import os
import netifaces
from uuid import getnode as get_mac

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

    def getnumber(self):
        mac = get_mac()
        h = iter(hex(mac)[2:].zfill(12))
        mac_addr = ":".join(i + next(h) for i in h)
        print("macadd : "+ mac_addr)
        return mac_addr



