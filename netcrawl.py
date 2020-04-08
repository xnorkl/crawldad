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

  def rootname(self) -> str:
    return self.root.hostname()

  def append(self, node) -> None:
    self.nodes.append(node)

class net_obj(base):
  #TODO: make setters
  
  def __init__(self, host, plat, ipv4, vlan, netd) -> None:
    self._host = host
    self._type = plat
    self._ipv4 = ipv4
    self._vlan = vlan
    self._netd = netd.lower()

  @property
  def hostname(self):
    return self._host

  @property
  def platform(self):
    return self._type

  @property
  def address(self):
    return self._ipv4

  @property
  def vlan(self):
    return self._vlan

  @property
  def device(self):
    return self._netd
     
class default(net_obj):

  def __init__(self, file='monode.conf') -> None:
    #TODO: use decorator instead of initialising parser here.
    parser = configparser.ConfigParser()
    parser.read(file)
    self.file = file
    self.__dict__.update(parser.items('DEFAULT'))
    self.__dict__.pop('file')

  def hostname(self) -> str:
    return self.__dict__.get('host')

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
        'username' : 'changeme',
        'password' : 'changeme',
        'secret'   : 'changeme'
        }
   
      core = {**dev, **creds}
      handler = ConnectHandler(**core)
      
      return handler
  
    def as_netobj(neighbor) -> net_obj:
      
      # Define regex patterns as groups.
      pattern = [
          re.search(r"(?P<DEV>(?<=Device ID: ).\w+)", neighbor),
          re.search(r"(?P<IP>(?<=IP address: ).*)", neighbor),
          re.search(r"(?P<VLAN>(?<=Native VLAN: ).*)", neighbor),
          re.search(r"(?P<SWITCH>(?<=Capabilities: )\w+)", neighbor)]
     
      host, ip, vlan, type = [re and re.group(1) for re in pattern]
      
      # TODO: add functionality for other types of devices.
      # Create an object based on the device type.
      if pattern[:1]: 
        if type == 'Switch':
          return net_obj(host, dev.cisco_ios.name, ip, vlan, type)

    ####End of SubMethods####

    fpath = "{}.raw".format(root.hostname())
    if not local:
      handler = connect(n)
      handler.enable()
      raw = handler.send_command("sh cdp nei det")
      handler.disconnect()
    
      #TODO: pull out to sep function.
      if path.exists(fpath):
        remove(fpath)
      with open(fpath, 'w+') as f:
        f.write(raw)
    else:
      # Read raw_output file into memory.
      with open(fpath) as f:
        raw = f.read()
    
    # Split raw data into elements of raw text for each device.
    raw_nodes = raw.split("-------------------------")

    # Step twice since "sh cdp nei" gives duplicate output.
    nodes = list()
    for n in raw_nodes[::step]:
      # Transform raw text into a net_obj. Remove empty entries.
      node = as_netobj(n)
      if node:
        nodes.append(node)

    return nodes

  def adj_map(n):
    ''' Create an adjency list to use for graph modeling '''

    net = net_map(default(), n)
    adj = {net.root.hostname() : [node.__dict__ for node in net.nodes]}
    return adj

 
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

    
    


#TODO: Create a proces to remove duplicates from network object.



#con = cdp.connect()
#cdp.write_show_nei(c n)
n = cdp.neighbors(default(), local=True)

#pp.pprint(a)

