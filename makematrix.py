import re
import sys
import pdb
import networkx as nx
import pylab

func_names = open("funcs_"+sys.argv[1]+".txt", "r")
func_names = list(func_names)
func_names  = [func.split(' ')[1][:-1] for func in func_names]
no_of_funcs = len(func_names)

cfg = open(sys.argv[1]+".c.011t.cfg",  "r")
cfg = list(cfg)

asm = open(sys.argv[1]+".s", "r")
asm = list(asm)
functions = dict([(i, '') for i in func_names])
func_name = ''

funcname_regex = re.compile(r'<([A-Za-z_0-9]+)>:$')
flag = 0
for instr in asm:
	match = re.search(funcname_regex, instr)
	if match and func_names.__contains__(match.group(1)):
		flag = 1
		currFunc = []
		func_name = match.group(1)
		continue

	if flag == 1:
		if instr != '\n':
			currFunc += [instr]
		else :
			functions[func_name] = currFunc
			flag = 0

jump_regex = re.compile(r'                	(j[a-z]*) *([a-f0-9]+)')
addr_regex = re.compile(r'([0-9a-f]+):\t')
split_funcs = []
jump_targets_all = []
graph_no = 0
for func_name, instructions in functions.iteritems():
	split_funcs += [dict()]
	jump_targets = []
	addr_match = re.search(addr_regex, instructions[0])
	jump_targets += [addr_match.group(1)]
	flag = 0
	for instr in instructions:
		jump_match = re.search(jump_regex, instr)
		if jump_match:
			jump_targets += [jump_match.group(2)]
			flag = 1
			continue
		if flag == 1:
			addr_match = re.search(addr_regex, instr)
			if jump_targets.__contains__(addr_match.group(1)) == 0:
				jump_targets += [addr_match.group(1)]
			flag = 0

	bbs = dict()
	bbs[0] = ["Entry"]
	curr_block = 0
	for instr in instructions:
		addr_match = re.search(addr_regex, instr)
		if jump_targets.__contains__(addr_match.group(1)):
			curr_block += 1
			bbs[curr_block] = []
			bbs[curr_block] += [instr] 
		else:
			bbs[curr_block] += [instr]
	split_funcs[graph_no] = bbs
	jump_targets_all += [sorted(set(jump_targets))]
	graph_no += 1


G = dict()
graph_no = 0
pdb.set_trace()
for func_name, bbs in split_funcs:
	G[graph_no] = nx.DiGraph()
	no_of_blocks = len(bbs)
	G[graph_no].add_node(0)
	for i in range(1, no_of_blocks):
		G[graph_no].add_node(i)
	
	G[graph_no].add_edge(0, 1)
	for i in range(1, no_of_blocks - 1):
		bb = bbs[i]
		jump_match = re.search(jump_regex, bb[-1])
		if jump_match:
			if jump_match.group(1) == 'jmp':
				j = jump_targets_all[graph_no].index(jump_match.group(2))
				G[graph_no].add_edge(i, j+1)
			else :	
				j = jump_targets_all[graph_no].index(jump_match.group(2))
				G[graph_no].add_edge(i, j+1)
				G[graph_no].add_edge(i, i+1)
		else:
			G[graph_no].add_edge(i, i+1)
	graph_no += 1

for i in range(no_of_funcs):
	graph = open("./graphs/graph"+str(i+1), "w")
	address = open("./graphs/addr"+str(i+1), "w")
	no_of_nodes = len(G[i].nodes())
	edges = G[i].edges().keys()
	no_of_edges = len(edges)
	graph.write(str(no_of_nodes) + " " + str(no_of_edges)+'\n')
	for a, b in iter(edges):
		graph.write(str(a) + " " + str(b)+'\n')
	jump_targets = jump_targets_all[i]
	for target in jump_targets:
		address.write(target + '\n')
	graph.close()
	address.close()
