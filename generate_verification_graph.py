import sys
import re
import networkx as nx
import pylab 
import pdb

modasm = open('labelled_'+sys.argv[1]+'.s', 'r')
# modasm = open('testing.txt','r')
modasm = list(modasm)
funcs = open("processed_funcs_"+sys.argv[1] + ".txt", "r")
funcs = list(funcs)
functions = dict()
for line in funcs:
	func, no_of_args = line.split('\t')
	no_of_args = int(no_of_args[:-1])
	functions[func] = no_of_args

func_regex = re.compile(r'([A-Za-z0-9_]+):\n')
jump_regex = re.compile(r'\tjmp\t.(jump_([A-Za-z0-9_]+)_....)\n')
called_regex = re.compile(r'\tjmp\t.(call_([A-Za-z0-9_]+)_....)\n')

verG = nx.DiGraph()
modasm = modasm[63:]
for line in modasm:
	func_match = re.search(func_regex, line)
	called_match = re.search(called_regex, line)
	jump_match = re.search(jump_regex, line)
	if func_match and functions.has_key(func_match.group(1)):
		curr_func = func_match.group(1)
	elif called_match and functions.has_key(called_match.group(2)):
		called_label = called_match.group(1)
		called_func = called_match.group(2)
		if not verG.has_node(called_func):
			verG.add_node(called_func)
		verG.add_edge(curr_func, called_func, label=called_label)
	elif jump_match:
		jump_label = jump_match.group(1)
		jump_loc = jump_match.group(2)
		verG.add_node(jump_loc)
		verG.add_edge(curr_func, jump_loc, label=jump_label)
# pos = nx.spring_layout(verG)
# edge_labels=nx.get_edge_attributes(verG, 'label')
# nx.draw(verG, with_labels=True)
# nx.draw_networkx_edge_labels(verG, pos,  edge_labels=edge_labels)	  
# pylab.show()
# pdb.set_trace()
# pdb.set_trace()