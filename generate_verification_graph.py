import sys
import re
import networkx as nx
from insert_labels import functions, func_regex, modasm

jump_regex = re.compile(r'\tjmp\t.(jump_[A-Za-z0-9_]+)\n')
called_regex = re.compile(r'\tjmp\t.(call_[A-Za-z0-9_]+)\n')
ret_regex = re.compile(r'\tjmp\t.(ret_[A-Za-z0-9_]+)\n') # put into monitor.py

verG = nx.Graph()
modasm = modasm[63:]

for line in modasm:
  func_match = re.search(func_regex, line)
  called_match = re.search(called_regex, line)
  jump_match = re.search(jump_regex, line)
  
  if func_match and functions.has_key(func_match.group(1)):
    curr_func = func_match.group(1)
    G.add_node(curr_func)
