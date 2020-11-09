#!/usr/bin/env python
from enum import Enum
from netmiko import ConnectHandler
import netmiko
import logging
import re
from typing import Dict
import config
import configparser
from os import path, remove
from collections import deque
import pprint as pp
from abc import ABC, abstractmethod
import uuid
from pathlib import Path
import networkx as nx

logging.basicConfig(filename='./test.log', level=logging.DEBUG)
logger = logging.getLogger("netmiko")

# Enumerated types for device platform and type of device.
dev = Enum('dev','cisco_ios cisco_asa_ssh cisco_s300 linux_ssh')
netdevice = Enum('netdevice', 'switch router server endpoint any')

# Abstract class for all network objects.

class base(object):
  
  def __init__(self):
    self._uuid = uuid.uuid4
    super().__init__()
  
class net_map():
    
  def __init__(self, root, nodes):
    self._root  = root
    self._nodes = nodes
 
  @property
  def root(self):
    return self._root

  @root.setter
  def root(self, val):
    if isinstance(val, net_obj): #TODO: isinstance(val, net_map) for tree
      self._root = val
    else:
      raise Exception("Expects a net_obj!")

  @property
  def nodes(self):
    return self._nodes

  @nodes.setter
  def nodes(self, val):
    if type(val) == list:
      self._nodes = val
    else:
      raise Exception("Expects a list!")

  def append(self, node):
    self.nodes.append(node)

  #TODO: Make this more useful (ie choose attr to display)
  def map(self):
    return {self.root.hostname : [n.hostname for n in self.nodes if n]}

  def sequence(self):
    r = self.root
    return [(r.hostname,n.hostname) for n in self.nodes if n]

class net_obj(base):
  #TODO: make setters
  
  def __init__(self, host, plat, ipv4, vlan, type):
    self._host = host
    self._plat = plat
    self._ipv4 = ipv4
    self._vlan = vlan
    self._type = type

  @property
  def hostname(self):
    return self._host.lower()

  @property
  def platform(self):
    return self._plat

  @property
  def address(self):
    return self._ipv4

  @property
  def vlan(self):
    return self._vlan

  @property
  def device(self):
    return self._type.lower()
     
class default(net_obj):
  
  def __init__(self):
    parser = configparser.ConfigParser()
    parser.read('monode.conf')
    self._host = parser['DEFAULT']['host']
    self._plat = parser['DEFAULT']['device_type']

class cdp:
  #TODO: Error checking on Type
  def neighbors(root, step=2, local=False) -> None:
    ''' store output of show neighbors detail '''

    ####SubMethods####
    #TODO: Get rid of submethods!

    def connect(node) -> None:
      ''' generate cdp connection handler '''
      
      # TODO: Handle creds correctly.
      dev = {
          'host': node.hostname,
          'device_type': node.platform
          }

      creds = {
        'username' : 'gordont',
        'password' : 'test123',
        'secret'   : 'change-mgh'
        }
   
      core = {**dev, **creds}
      handler = ConnectHandler(**core)
      
      return handler
  
    def as_netobj(neighbor) -> net_obj:
      
      # Define regex patterns as groups.
      pattern = [
          re.search(r"(?P<DEV>(?<=Device ID: ).[\w-]+)", neighbor),
          re.search(r"(?P<IP>(?<=IP address: ).[\d.]+)", neighbor), #TODO: Fix
          re.search(r"(?P<VLAN>(?<=Native VLAN: ).\d+)", neighbor),
          re.search(r"(?P<SWITCH>(?<=Capabilities: )[\w-]+)", neighbor)]
     
      host, ip, vlan, type = [re and re.group(1) for re in pattern]
      
      # Create an object based on the device type.
      if type:
        return net_obj(host, dev.cisco_ios.name, ip, vlan, type)

    ####End of SubMethods####
    foldr = Path('./raw/')
    rfile = '{}.raw'.format(root.hostname)
    fpath = foldr / rfile
    if local:
      try:
      # Read raw_output file into memory.
        with open(fpath) as f:
          raw = f.read()
      except OSError as e:
        print(e)
        return
    else:
      try:
        handler = connect(root)
        handler.enable()
        raw = handler.send_command("sh cdp nei det")
        handler.disconnect()
      except netmiko.ssh_exception.NetmikoTimeoutException as e:
        raise(e)
 
      #TODO: pull out to sep function.
      if path.exists(fpath):
        remove(fpath)
      with open(fpath, 'w+') as f:
        f.write(raw)
  
    # Split raw data into elements of raw text for each device.
    raw_nodes = raw.split("-------------------------")

    # Step twice since "sh cdp nei" gives duplicate output.
    nodes = [as_netobj(n) for n in raw_nodes[::step] if n]

    return net_map(root, nodes)
  
  def adj_matrix(n):
    ''' Take a network map and create and adjacency matrix '''

    net = net_map(default(), n)
    matrix = list()

    pass

#TODO: Create a queue or some other data structure to crawl neighbors.

  def build_deque(n):
    ''' Deque to track which neighbors have been crawled. '''
    
    stack = deque()
    for h in n:
      stack.append(h.hostname)

#TODO: Try Throw 
#TODO: Create a proces to remove duplicates from network object.


def edges():
  root_net = cdp.neighbors(default(), local=True)
  edges = root_net.sequence()
  for node in root_net.nodes:
    if node:
      try: 
        child_net = cdp.neighbors(node, local=True)
        for tuple in child_net.sequence():
          edges.append(tuple)
      except Exception as e:
        print("{}: {}".format(node.hostname, e))
        pass

  return edges
#G = nx.Graph(edges)
#print(G.nodes)



  

