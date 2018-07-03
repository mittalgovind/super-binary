import re
import sys
import random
import pdb
import networkx as nx
from get_control_graphs import jump_targets_all_raw
from getsecpoints import secpoints

def randhex():
	s = ''
	for i in range(16):
		s += str(random.randint(0, 1))
	s = hex(int(s, 2))
	s = s[2:]
	if len(s) == 3:
		s = '0' + s
	return '_' + s

asm = open(sys.argv[1] + ".s", "rw+")
asm = list(asm)
funcs = open("processed_funcs_"+sys.argv[1] + ".txt", "r")
funcs = list(funcs)
functions = dict()
for line in funcs:
	func, no_of_args = line.split('\t')
	no_of_args = int(no_of_args[:-1])
	functions[func] = no_of_args


func_regex = re.compile(r'^([A-Za-z0-9_]+):')
called_regex = re.compile(r'\tcall\t([A-Za-z0-9_]+)')
jump_regex = re.compile(r'\t(j[a-z]+)\t.([A-Za-z0-9]+)')
ret_regex = re.compile(r'\tleave\n')
modasm = asm[0:63]
asm = asm[63:]
insert_pos = 0
curr_func = ''

def put(input_str):
	global insert_pos
	modasm.insert(insert_pos, input_str)
	insert_pos += 1

for i, line in enumerate(asm):
	func_match = re.search(func_regex, line)
	called_match = re.search(called_regex, line)
	jump_match = re.search(jump_regex, line)
	ret_match = re.search(ret_regex, line)
	if func_match and functions.has_key(func_match.group(1)):
		curr_func = func_match.group(1)
		jump_count = 0
		if ".text" in asm[i - 3]:
			insert_pos = len(modasm) - 2
			modasm.insert(-3, "	.section	.rodata\n")
		else:
			insert_pos = len(modasm) - 1
			modasm.insert(-2, "	.section	.rodata\n")
		modasm.append(line)
		if "main:" in line:
			put('.func_main:\n')
			put('\t.string\t\"call_main\"\n')
			put('.call_main:\n')
			put('\tpushl\t$.func_main\n')
			put('\tcall\tvErIfY\n')
			put('\tjmp\t.retcall_main\n')
			modasm.append('\tcall\tinit_file_for_vErIfY\n')
			modasm.append('\tjmp\t.call_main\n')
			modasm.append('.retcall_main:\n')


	elif called_match and functions.has_key(called_match.group(1)):
		no_of_args = functions[called_match.group(1)]
		randstr = randhex()
		call_label = 'call_' + called_match.group(1) + randstr
		put('.str'+randstr+":\n\t.string\t\""+call_label +"\"\n")
		put('.'+call_label + ":\n")
		put('\tpushl\t$.str'+randstr+"\n")
		put('\tcall\tvErIfY\n')
		while no_of_args > 0:
			put(modasm.pop())
			no_of_args -= 1
		put(line)
		put('\tjmp\t.ret'+call_label +"\n")
		modasm.append('\tjmp\t.' + call_label +"\n")
		modasm.append('.ret'+call_label +":\n")

	elif jump_match:
		jump_count += 1
		for addr, count in jump_targets_all_raw[curr_func]:
			if addr in secpoints and count == jump_count:
				randstr = randhex()
				jump_label = 'jump_' + jump_match.group(2) + randstr 
				put('.str'+randstr+":\n\t.string\t\""+jump_label+"\"\n")
				put('.'+jump_label+":\n")
				put('\tpushl\t$.str'+randstr+"\n")
				put('\tcall\tvErIfY\n')
				put(modasm.pop())
				put(line)
				put('\tjmp\t.ret'+jump_label+ '\n')
				modasm.append('\tjmp\t.' + jump_label+"\n")
				modasm.append('.ret'+jump_label+ ":\n")
			else:
				modasm.append(line)
				break
	elif ret_match and curr_func != '' :
		put('.funcname_' + curr_func +":\n")
		put('\t.string\t\"ret_' + curr_func + '\"\n')
		put('.ret_'+ curr_func + ':\n')
		# put('\tpushl\t$1'+'\n')
		put('\tpushl\t$.funcname_'+curr_func+'\n')
		put('\tcall\tvErIfY\n')
		put('\tjmp\t.end_'+curr_func+'\n')
		modasm.append('\tjmp\t.ret_'+curr_func+'\n')
		modasm.append('.end_'+curr_func+':\n')
		modasm.append(line)
	else:
		modasm.append(line)

labelledasm = open("labelled_" + sys.argv[1] + ".s", "w")
for line in modasm:
	labelledasm.write(line)
labelledasm.close()
