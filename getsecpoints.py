import re
import pdb

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
			secpoints +=  [addr[index - 1][:-1]]
		else:
			secpoints += [addr[0][:-1]]

secpoints.sort()
print(secpoints)