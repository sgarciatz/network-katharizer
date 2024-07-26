from Kathara.model.Lab import Lab
from Kathara.model.Link import Link
from enum import Enum
import ipaddress as ip

class LinkType(Enum):
    HOSTS       = 1
    CONNECTION  = 2

class TedLink(Link):

    def __init__(self, lab: Lab, name: str, linkType: LinkType):
        super().__init__(lab,name)
        self.type = linkType
        
    def __repr__(self) -> str:
        
#        machineNames = list(map(lambda machine: machine.name, self.machines))
        return "Link(%s, %s)" % (self.name, self.external)
        

