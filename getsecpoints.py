import re
import pdb
import sys
import random
from get_control_graphs import jump_targets_all_raw

def randhex():
	s = ''
	for i in range(16):
		s += str(random.randint(0, 1))
	s = hex(int(s, 2))
	return '_' + s[2: ]

regex = re.compile(r'^(\d+)\n')
endex = re.compile(r'\*\*\*\* no errors detected')
results = open("results", "r")
results = list(results)
graph_no = 1
secpoints = []
for line in results:
	addr = open("graphs/addr"+str(graph_no), "r")
	addr = list(addr)
	match = re.search(regex, line)
	end = re.search(endex, line)
	if end: 
		graph_no += 1
		continue
	if match:
		index = int(match.group(1))
		if index < len(addr):
			secpoints += [addr[index - 1][:-1]]
		else:
			secpoints += [addr[0][:-1]]

print secpoints
# jump_targets_all_raw = {'Eprime': [('8048a83', 1)], 'E': [], 'Tprime': [('80489b3', 1)], 'T': [('8048978', 1), ('8048964', 2)], 'main': [('8048910', 1), ('8048910', 2), ('8048925', 3)], 'check': [('80489f2', 1), ('8048a53', 2), ('8048a49', 3), ('8048a3d', 4), ('8048a53', 5), ('8048a53', 6)]}
# secpoints = ['8048932', '8048a56', '8048978', '8048986', '80489b6', '80489f2', '8048a02', '804887c']
asm = open(sys.argv[1] + ".s", "rw+")
asm = list(asm)
funcs = open("processed_funcs_"+sys.argv[1] + ".txt", "r")
funcs = list(funcs)
functions = dict()
for line in funcs:
	func, no_of_args = line.split('\t')
	no_of_args = int(no_of_args[:-1])
	functions[func] = no_of_args

func_regex = re.compile(r'([A-Za-z0-9_]+):')
called_regex = re.compile(r'\tcall\t([A-Za-z0-9_]+)')
jump_regex = re.compile(r'\t(j[a-z]+)\t.([A-Za-z0-9]+)')
curr_func = ''
modasm = []
insert_pos = 0
for i, line in enumerate(asm):
	func_match = re.search(func_regex, line)
	called_match = re.search(called_regex, line)
	jump_match = re.search(jump_regex, line)
	if func_match and functions.has_key(func_match.group(1)):
		curr_func = func_match.group(1)
		jump_count = 0
		# pdb.set_trace()
		if ".text" in asm[i - 3]:
			insert_pos = len(modasm) - 2
			modasm.insert(-3, "	.section	.rodata\n")
		else:
			insert_pos = len(modasm) - 1
			modasm.insert(-2, "	.section	.rodata\n")
		modasm.append(line)
	elif called_match and functions.has_key(called_match.group(1)):
		no_of_args = functions[called_match.group(1)]
		randstr = randhex()
		modasm.insert(insert_pos, '.call_' + called_match.group(1) + randstr +":\n")
		insert_pos += 1
		while no_of_args > 0:
			modasm.insert(insert_pos, modasm.pop())
			no_of_args -= 1
			insert_pos += 1
		modasm.insert(insert_pos, line)
		insert_pos += 1
		modasm.insert(insert_pos, '\tjmp\t.retcall_' + called_match.group(1) + randstr +"\n")
		insert_pos += 1

		modasm.append('\tjmp\t' + '.call_' + called_match.group(1) + randstr +"\n")
		modasm.append('.retcall_' + called_match.group(1) + randstr +":\n")

	elif jump_match:
		jump_count += 1
		for addr, count in jump_targets_all_raw[curr_func]:
			if addr in secpoints and count == jump_count:
				randstr = randhex()
				modasm.insert(insert_pos, '.jump_' + jump_match.group(2) + randstr +":\n")
				insert_pos += 1
				modasm.insert(insert_pos, modasm.pop())
				insert_pos += 1
				modasm.insert(insert_pos, line)
				insert_pos += 1
				modasm.insert(insert_pos, '\tjmp\t.retjump_' + jump_match.group(2) + randstr + '\n')
				insert_pos += 1
				modasm.append('\tjmp\t' + '.jump_' + jump_match.group(2) + randstr +"\n")
				modasm.append('.retjump_' + jump_match.group(2) + randstr + ":\n")
			else:
				modasm.append(line)
				break
	else:
		modasm.append(line)

labelledasm = open("labelled_" + sys.argv[1] + ".s", "w")
for line in modasm:
	labelledasm.write(line)
labelledasm.close()