from Kathara.model.Lab import Lab
import pandas as pd
import numpy as np
from TedMachine import TedMachine, MachineType
from TedLink import TedLink, LinkType
import math
import ipaddress as ip
from Kathara.manager.Kathara import Kathara
import os
import igraph as ig
import time
from enum import Enum

class ExecutionMode(Enum):


    """Different execution modes for the Kathara experiments"""

    NORMAL = 1
    SCALABLE = 2

class TedLab(Lab):


    """TedLab is the responsable of seting up the input data
    to carry out the experiment in Kathara
    """

    def __init__(self, configurationFile: str, name: str,
                 path: str, mode: ExecutionMode):

        if not os.path.exists(path):
            os.makedirs(path)
        super().__init__(name, path)
        self.path = path
        self.create_shared_folder()
        self.general_options["image"] = 'santiagogg/ted:kathara_quagga_light-v2'
        self.mode = mode

        # Read the information from the configuration file
        self.loadExperimentData(configurationFile)
        self.nDrones = len(self.configuration.index)
        self.nMs = ((len(self.configuration.columns) - self.nDrones - 1) // 3)
        self.adjMatrix = self.configuration.iloc[:,-self.nDrones:].to_numpy()
        self.adjMatrix = np.tril(self.adjMatrix).T
        np.fill_diagonal(self.adjMatrix, 0)

        # Create all the machines
        self.createDevices()
        #Create all the links (collision domains)
        self.createConnections()
        # Assign an IP to each interface of each device
        self.configureConnections()




    def calcShortestPathCost(self):

        """Find the best server for each host"""

        hosts = list(filter(lambda host: host.type == MachineType.HOST,
                            self.machines.values()))
        routers = list(filter(lambda host: host.type == MachineType.ROUTER,
                              self.machines.values()))

        auxAdjMatrix = self.configuration.iloc[:,-self.nDrones:].to_numpy()
        a = pd.DataFrame(
                auxAdjMatrix,
                index=list(map(lambda router: router.name, routers)),
                columns=list(map(lambda router: router.name, routers)))
        g = ig.Graph.Adjacency(a)

        paths = []
        for v in g.vs:
            paths.append(g.get_shortest_paths(v, output = "vpath"))

        d2hLinks = list(filter(
              lambda link: link.type == LinkType.HOSTS,
              self.links.values()))

        for link in d2hLinks:
            srcRouter = list(link.machines.values())[0]
            srcIndex = int(srcRouter.name[srcRouter.name.rfind('_')+1:])
            for host in list(link.machines.values())[1:]:
                costAndDst = []
                hostIndex = int(host.name[host.name.rfind('_')+1:])
                for dstRouter in routers:
                    dstIndex =\
                        int(dstRouter.name[dstRouter.name.rfind('_')+1:])
                    pathCost = len(paths[srcIndex][dstIndex])
                    canServe = self.configuration\
                                        .loc[dstIndex].iloc[hostIndex+1] == 1
                    if (pathCost == 0 and canServe):
                        machineIp = dstRouter.network_ips[0]['machine_ip']
                        costAndDst.append({'dst': machineIp,
                                           'cost': pathCost})
                    elif (pathCost > 0 and canServe):
                        machineIp = dstRouter.network_ips[0]['machine_ip']
                        costAndDst.append({'dst': machineIp,
                                           'cost': pathCost})
                bestServer = min(costAndDst,
                                 key=lambda element: element['cost'])
                host.add_meta('dst', bestServer['dst'])


    def loadExperimentData(self, filePath: str) -> None:

        """Parse the input file to set up the experiment"""

        self.configuration = pd.read_csv(filePath)

    def createDevices(self) -> None:

        """Create all the routing devices and end user devices

        In NORMAL mode one host is created for each microservice and
        routing device.
        In SCALABLE mode host are only created for the microservices
        with a heat value greater than 0."""

        firstColumn: int = self.nMs + 1
        lastColumn: int = (self.nMs * 2) + 1
        self.subnets = []
        # For each UAV, create one subnet
        for index, row in self.configuration.iterrows():
            subnet = []
            droneId: str = f'drone_{index}'
            self.machines[droneId] = TedMachine(self,
                                                droneId,
                                                MachineType.ROUTER)
            subnet.append(self.machines[droneId])
            # For each subnet, create the hosts
            for j, ms in enumerate(row[firstColumn:lastColumn]):
                hostId: str = f'host_d{index}_{j}'
                isNormalMode = (self.mode == ExecutionMode.NORMAL)
                isScalableMode = (self.mode == ExecutionMode.SCALABLE)\
                                 and ms > 0

                if (isNormalMode or isScalableMode):
                    self.machines[hostId] = TedMachine(self,
                                                   hostId,
                                                   MachineType.HOST)
                    subnet.append(self.machines[hostId])
            self.subnets.append(subnet)

    def createConnections(self) -> None:

        """Create the connections between routing devices and hosts"""

        # Create the drone2host links and attach devices to them
        for subnet in self.subnets:
            subnetName: str = f'link_{subnet[0].name}_hosts'
            self.links[subnetName] = TedLink(self,
                                             subnetName,
                                            LinkType.HOSTS)
            for device in subnet:
                device.add_interface(self.links[subnetName])
        # Create the drone2host links and attach it to the drones
        for i, row in enumerate(self.adjMatrix):
            for j, cell in enumerate(row):
                if (cell == 1):
                    drone1 = self.machines[f'drone_{i}']
                    drone2 = self.machines[f'drone_{j}']
                    subnetName = f'link_drone{i}_drone{j}'
                    self.links[subnetName] = TedLink(self,
                                                     subnetName,
                                                     LinkType.CONNECTION)
                    drone1.add_interface(self.links[subnetName])
                    drone2.add_interface(self.links[subnetName])

    def configureConnections(self) -> None:

        """Assign the IP and the gateway to each interface and ping
        script if needed"""

        ipAddress = ip.IPv4Address('129.0.0.0')
        orderedLinks = list(self.links.values())
        orderedLinks.sort(reverse=True, key=lambda link: len(link.machines))

        for link in orderedLinks:
            mask = 32 - math.ceil(math.log2(len(link.machines)+2))
            network = ip.IPv4Network(f'{ipAddress}/{mask}')
            hostsIp = list(network.hosts())
            ipAddress = network.broadcast_address + 1
            for device, newIp in zip(link.machines, hostsIp):
                self.machines[device].addNetworkInterface(newIp, network)

        # Find the server for each user
        self.calcShortestPathCost()

        d2hLinks = list(filter(
              lambda link: link.type == LinkType.HOSTS,
              self.links.values()))

        for link in d2hLinks:
            router = list(link.machines.values())[0]
            routerIp = router.network_ips[0]['network'].network_address + 1
            routerIndex = int(router.name[router.name.rfind('_')+1:])
            router.add_meta('exec', '/etc/init.d/quagga start')
            for host in list(link.machines.values())[1:]:
                hostIndex = int(host.name[host.name.rfind('_')+1:])
                column = self.nMs + 1 + hostIndex
                heat = self.configuration.loc[routerIndex].iloc[column]
                host.add_meta('heat', heat)
                if (heat > 0): host.createPingingScript()
                host.add_meta('exec', f"route add default gw {str(routerIp)}")

    def executePythonPings(self, containers) -> None:

        """Write the files into the containers and execute them"""

        hosts = self.mergeContainerToDevice(containers)
        print(f'Executing {len(hosts)} pings!')
        timeRef = time.time()
        for (container,_) in hosts:
            cmd = 'python3 /home/pingingScript.py'
            container.exec_run(cmd, detach=True)
        print(f'Execution done! {time.time() - timeRef} s')

    def executeBashPings(self, containers) -> None:

        """Prepare the execution parameters for each pinging script"""

        hosts = self.mergeContainerToDevice(containers)
        print(f'Executing {len(hosts)} pings!')
        timeRef = time.time()
        for (container, device) in hosts:
            heat = device.meta['heat']
            dstIP = device.meta['dst']
            cmd = 'bash /home/pingingScript.sh'\
                  + f' {dstIP}' + f' {heat}'\
                  + f' {device.name}'
            container.exec_run(cmd, detach=True)
        print(f'Execution done! {time.time() - timeRef} s')

    def mergeContainerToDevice(self, containers) -> list:

        """Creates a list with the Docker containers and it asociated
        TedMachines"""

        filteredHosts = list(filter(
            lambda host: host.type == MachineType.HOST
                         and 'heat' in host.meta,
            self.machines.values()))
        filteredContainers = []
        for container in containers:
            for host in filteredHosts:
                if (f'_{host.name}_' in container.name):
                    filteredContainers.append(container)
                    break
        mergedData = []
        for container in filteredContainers:
            for host in filteredHosts:
                hostName = f'_{host.name}_'
                if (hostName in container.name):
                    mergedData.append((container, host))
                    filteredHosts.remove(host)
                    break
        return mergedData

    def getSummary(self) -> str:

        """Returns a string that summarizes the scenario"""

        hosts = list(filter(lambda host: host.type == MachineType.HOST,
                            self.machines.values()))
        routers = list(filter(lambda host: host.type == MachineType.ROUTER,
                              self.machines.values()))
        d2hLinks = list(filter(
                      lambda link: link.type == LinkType.HOSTS,
                      self.links.values()))
        d2dLinks = list(filter(
                             lambda link: link.type == LinkType.CONNECTION,
                             self.links.values()))
        summary = f'Experiment {self.name}:\n'\
                  + f'\t-Devices: {len(hosts) + len(routers)}\n'\
                  + f'\t\t+Drones: {len(routers)}\n'\
                  + f'\t\t+Hosts: {len(hosts)}\n'\
                  + f'\t-Links: {len(d2dLinks) + len(d2hLinks)}\n'\
                  + f'\t\t+Drone2drone link: {len(d2dLinks)}\n'\
                  + f'\t\t+Drone2host Link: {len(d2hLinks)}\n'
        return summary


def main(args):
    configuration = args.input_file
    lab_folder = args.output_file
    execution_mode = ExecutionMode(args.mode)
    myLab = TedLab(configuration,
                'Santiago',
                os.path.join(os.getcwd(), lab_folder),
                execution_mode)
    myLab.check_integrity()
    print(myLab.getSummary())

    print('Deploying Kathara lab...')

    myKathara = Kathara.get_instance()
    myKathara.deploy_lab(myLab)
    print('Done!')

    sleepingTime = 300
    print(f'Waiting {sleepingTime} seconds to let OSPF converge.')
    time.sleep(sleepingTime)
    client = docker.from_env()
    conts = client.containers.list()
    myLab.executeBashPings(conts)
    print('Wait at least 300 seconds and Look in',
          f'{lab_folder}/shared/ for output')


if __name__ == "__main__":
    import docker, time, argparse
    parser = argparse.ArgumentParser(
                prog='NetworkKatharizer',
                description=('Creates a virtual replica of a network.'
                             'Specify an input file, output file and the'
                             'execution mode: 1 for normal and 2 for'
                             'scalable'))
    parser.add_argument('input_file', type=str)
    parser.add_argument('output_file', type=str)
    parser.add_argument('mode', type=int)
    args = parser.parse_args()
    main(args)