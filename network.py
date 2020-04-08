#!/usr/bin/env python
from netmiko import ConnectHandler
import netmiko
import networkx as nx
import logging
import re
import pprint as pp
import matplotlib.pyplot as plt

logging.basicConfig(filename='./test.log', level=logging.DEBUG)
logger = logging.getLogger("netmiko")

cred = ['gordont','test123','change-mgh']
host = ['cisco_ios','1st_nt_mdf_sw01.mhs.org']

def cdp_neighbors(device: str, host: str, cred: list) -> str:
  ''' generate cdp connection handler and return dict '''
  #TODO: make cred a Type

  switch = {
      'device_type' : device,
      'host'        : host,
      'username'    : cred[0],
      'password'    : cred[1],
      'secret'      : cred[2]
      }

  # Create connection to switch and set enable mode on.
  netcon = ConnectHandler(**switch)
  netcon.enable()

  nei_raw = netcon.send_command("sh cdp nei det")

  return nei_raw

def child_objects(nei_raw: str) -> list:
  ''' create a dict from switch cdp responses '''

  # Parse raw data.
  rdata = nei_raw.split("-------------------------")

  # Step twice since "sh cdp nei" gives duplicate output.
  nei_map = list()
  for d in rdata[::2]:

    # Define regex patterns as groups.
    dev   = re.search(r"(?P<DEV>(?<=Device ID: ).\w+)",d)
    ip    = re.search(r"(?P<IP>(?<=IP address: ).*)",d) #better regex
    vlan  = re.search(r"(?P<VLAN>(?<=Native VLAN: ).*)",d) # ...
    type  = re.search(r"(?P<SWITCH>(?<=Capabilities: )\w+)",d) #use for recur

    node = dict()
    node['DATA'] = dict()

    if dev:
      node['NODE_ID'] = dev.group(1)
    if ip:
      node['DATA']['IP'] = ip.group(1)
    if type:
      node['DATA']['TYPE'] = type.group(1)
    if vlan:
      node['DATA']['VLAN'] = vlan.group(1)
    # Remove empty entries.
    if node['DATA']:
      nei_map.append(node)

  return nei_map

def graph_network(p: str, children: list) -> dict:

  p_c = [(p,c['NODE_ID']) for c in children]

  G = nx.Graph()
  G.add_edges_from(p_c)
  return G

with open('raw') as f:
  raw_data = f.read()

map = child_objects(raw_data)

graph = graph_network(host[1],map)
pp.pprint("Nodes: {}\nEdges: {}".format(graph.nodes, graph.edges))

nx.draw_shell(graph, with_labels=True)
plt.show()

#graph = graph_network(host)

#print(graph.nodes)
#print(graph.edges)
#test = "Device ID: MGH1A-CORE.mongeneral.com\nEntry address(es):\nIP address: 172.26.2.122\nPlatform: cisco WS-C4507R+E,  Capabilities: Switch IGMP\nInterface: TenGigabitEthernet2/0/24,  Port ID (outgoing port):TenGigabitEthernet4/1\nHoldtime : 150 sec\nadvertisement version: 2\nVTP Management Domain: 'MonGen'\nNative VLAN: 666\nDuplex: full\nManagement address(es):\n  IP address: 172.26.2.122\n\n-------------------------\nDevice ID:MGH1-CORE.mongeneral.com\nEntry address(es):\n  IP address: 172.26.2.22\nPlatform: cisco WS-C4507R+E,  Capabilities: Switch IGMP\nInterface: TenGigabitEthernet1/0/24,  Port ID (outgoing port):TenGigabitEthernet3/1\nHoldtime : 150 sec\nadvertisement version: 2\nVTP Management Domain: 'MonGen'\nNative VLAN: 66\nDuplex: full\nManagement address(es):\n  IP address: 172.26.2.12"


#print(get_entry(test))

