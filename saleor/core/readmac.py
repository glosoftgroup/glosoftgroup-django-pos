import sys
import os
import netifaces
from uuid import getnode as get_mac
import subprocess,time,socket
from Crypto.Util.Counter import new
from Crypto.Cipher import AES
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

    def getnumber(self):
        mac = get_mac()
        h = iter(hex(mac)[2:].zfill(12))
        mac_addr = ":".join(i + next(h) for i in h)
        print("macadd : "+ mac_addr)
        if sys.platform == 'win32':
            mac_addr = self.windows()
            return mac_addr
        return mac_addr

    def windows(self):
        BLOCK_SIZE = 32
        PADDING = '{'
        pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING
        EncodeAES = lambda c, s: base64.b64encode(c.encrypt(pad(s)))
        DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(PADDING)

        machine_id = subprocess.check_output('wmic csproduct get UUID').split('\n')[1].strip()
        machine_model_number = subprocess.check_output('wmic csproduct get IdentifyingNumber').split('\n')[1].strip()
        new_id = '*!%F{0}@/{1}*'.format(machine_id, machine_model_number)

        # salt = b'!%F=-?Pst970'
        salt = str(new_id)
        bkey32 = salt.ljust(32)[:32]
        return bkey32
        # cipher = AES.new(bkey32, AES.MODE_ECB)
        # print cipher

        # # encode a string
        # encoded = EncodeAES(cipher, 'secret')
        # print 'Encrypted string:', encoded

        # # decode the encoded string
        # decoded = DecodeAES(cipher, encoded)
        # print 'Decrypted string:', decoded



