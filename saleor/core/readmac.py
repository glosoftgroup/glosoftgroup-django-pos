import sys
import os
import netifaces
from uuid import getnode as get_mac
import subprocess,time,socket
import base64


class FetchMac():

    def __init__(self):
        pass

    def format_machine(self, new_id):
        formatted = str(new_id)
        bb = base64.b64encode(bytes(formatted))
        bkey322 = bb.ljust(32)[:32]
        return bkey322

    def getnumber(self):
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
        mid = os.environ.get('MACHINE_ID')
        if not mid:
            os.environ['MACHINE_ID'] = str(self.format_machine(new_id))
            mid = os.environ.get('MACHINE_ID')
            if mid == '':
                mid = 'NOT SET'
        return mid

    def unix(self):
        machine_id = subprocess.check_output("dmesg | grep Kernel | sed s/.*UUID=//g | sed s/\ ro\ quiet.*//g", shell=True)
        new_id = '{0}'.format(machine_id)
        mid = os.environ.get('MACHINE_ID')
        if not mid:
            os.environ['MACHINE_ID'] = str(self.format_machine(new_id))
            mid = os.environ.get('MACHINE_ID')
            if mid == '':
                mid = 'NOT SET'
        return mid

    def mac(self):
        machine_id = subprocess.check_output("ioreg -rd1 -c IOPlatformExpertDevice | grep -E '(UUID)'", shell=True)
        new_id = '*!%F{0}@*'.format(machine_id)
        mid = os.environ.get('MACHINE_ID')
        if not mid:
            os.environ['MACHINE_ID'] = str(self.format_machine(new_id))
            mid = os.environ.get('MACHINE_ID')
            if mid == '':
                mid = 'NOT SET'
        return mid



