import configparser
import functools
import inspect
from enum import Enum
from os import path

def init_parser(cls):
  cls.name = str(cls)
  cls.parser = configparser.ConfigParser()
  return cls

def check_file(f):
  @functools.wraps(f)
  def wrapper(*args: str, **kwargs: str):
    func_args = inspect.getcallargs(f, *args, **kwargs)
    if func_args.get('file') != 'monode.conf':
      raise Exception("Configurations must be read from monode.conf!")
    else:
      if path.exists('monode.conf'):
        if f.__name__ == 'make':
          pass
        elif f.__name__ == 'read':
          return f(*args, **kwargs)
        else:
          raise Exception ("Non-applicable function!")
    return wrapper

@init_parser
class config():
  ''' Currently Bare Bones '''
  def __init__(self, file='monode.conf'):
    self.file = file

  @check_file
  def make(core_switch: dict):
      parser['CORE'] = core_switch
      with open('monode.conf', 'w') as conf:
        config.write(conf)

  @check_file
  def read() -> str:
    return parser['CORE']

