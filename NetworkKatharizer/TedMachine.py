from Kathara.model.Machine import Machine
import numpy as np
from enum import Enum
import ipaddress as ip
import os

class MachineType(Enum):
    HOST    = 1
    ROUTER  = 2


class TedMachine(Machine):

    def __init__(self, lab: 'LabPackage.Lab',
                 name: str,
                 machineType: MachineType,
                 **kwargs):
        super().__init__(lab, name, cpus=1, mem='10m')

        self.network_ips = []
        self.networks = []
        self.type = machineType
        self.lastAssignedInterface = 0

        self.deamons_file = ['# This file tells the quagga package ',
                            '# which daemons to start.',
                            '# Entries are in the format: <daemon>=(yes|no|priority)',
                            '# where \'yes\' is equivalent to infinitely low priority, and',
                            '# lower numbers mean higher priority. Read',
                            '# /usr/doc/quagga/README.Debian.gz for details.',
                            '# Daemons are: bgpd zebra ospfd ospf6d ripd ripngd',
                            'zebra=yes',
                            'bgpd=no',
                            'ospfd=yes',
                            'ospf6d=no',
                            'ripd=no',
                            'ripngd=no'
                            ]

        self.zebra_file  =[ '! -*- zebra -*-',
                         '!',
                         '! zebra configuration file',
                         '!',
                         f'hostname {self.name}',
                         'password zebra',
                         'enable password zebra',
                         '!',
                         '! Static default route sample.',
                         '!',
                         '!ip route 0.0.0.0/0 203.181.89.241',
                         '!',
                         'log file /var/log/quagga/zebra.log'
                         ]

#        self.ripd_conf   =[ '!',
#                         'hostname ripd',
#                         'password zebra',
#                         'enable password zebra',
#                         '!',
#                         'router rip',
#                         'redistribute connected',
#                         'network 129.0.0.0/8',
#                         'version 2',
#                         '!',
#                         'log file /var/log/quagga/ripd.log'
#                            ]
        self.ospfd_conf =[
                         'hostname ospfd',
                         'password zebra',
                         'router ospf',
                         'redistribute connected',
                         'network 129.0.0.0/8 area 0.0.0.0',
                         'log file /var/log/quagga/ospfd.log'
                         ]
        if (self.type == MachineType.ROUTER): self.createConfigurationFile()

    def createConfigurationFile(self):

        quagga_path = os.path.join('/', 'etc', 'quagga')

        self.create_file_from_list(self.deamons_file, os.path.join(quagga_path, 'daemons'))
        self.create_file_from_list(self.zebra_file, os.path.join(quagga_path, 'zebra.conf'))
#        self.create_file_from_list(self.ripd_conf, os.path.join(quagga_path, 'ripd.conf'))
        self.create_file_from_list(self.ospfd_conf, os.path.join(quagga_path, 'ospfd.conf'))

    def createPingingScript(self):
        script_lines = [
            'import time, threading, ping3, random',
            'import pandas as pd',
            f"WAIT_SECONDS = 1 / {self.meta['heat']}",
            'pings = []',
            'time_reference = time.time()',
            'duration = 60 ',

            'def ping_to_server():',
                '\tping_time = time.ctime()',
                '\trtt = ping3.ping(\'' + str(self.meta['dst']) + '\')',
                '\tpings.append([ping_time, rtt])',

            'def periodic_function():',
                '\tthreading.Thread(target=ping_to_server()).run()',
                '\tif time.time() - time_reference < duration:',
                    '\t\tthreading.Timer(WAIT_SECONDS, periodic_function).start()',
                '\telse:',
                    '\t\ttime.sleep(random.randint(600, 1200) / 10.0)',
                    "\t\tdf = pd.DataFrame(data=pings, columns=['Ping timestamp', 'RTT'])",
                    f"\t\tdf.to_csv('/shared/{self.name}')",

            'periodic_function()'
        ]
        self.create_file_from_list(script_lines, f'/home/pingingScript.py')

    def addNetworkInterface(self,
                            machine_ip: ip.IPv4Address,
                            net: ip.IPv4Network):
        self.network_ips.append({'machine_ip': machine_ip, 'network': net})
        cmd = f'ifconfig eth{self.lastAssignedInterface} '\
              + f'{machine_ip}/{net.prefixlen} up'
        self.add_meta('exec', cmd)
        self.lastAssignedInterface += 1

    def printLinksAlognsideIP(self):
        string = f'{self.name}:\n'

        for i, link in enumerate(self.interfaces):
            string += f'{self.interfaces[link].name}'
            string += f"\t {self.network_ips[i]['network']}"
            string += f"\t {self.network_ips[i]['machine_ip']} \n\n"

        return string
