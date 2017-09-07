import fcntl, socket, struct
import sys
import os

class FetchMac():

    def __init__(self):
        pass


    def getHwAddr(self, ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', ifname[:15]))
        return ':'.join(['%02x' % ord(char) for char in info[18:24]])

    def getmac(self, interface):

        try:
            mac = open('/sys/class/net/' + interface + '/address').readline()
        except:
            mac = "00:00:00:00:00:00"

        return mac[0:17]

    def getnumber(self):
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
            for line in os.popen("/sbin/ifconfig"):
                if line.find('ether') > -1:
                    mac = line.split()[4]
                    break
        return mac

    def test(self):
        print 'test'

    def getmacmac(self):
        macaddr = "00:00:00:00:00:00"

        for line in os.popen("/sbin/ifconfig"):
            if line.find('ether') > -1:
                macaddr = line.split()[-1]
                break

        return macaddr
