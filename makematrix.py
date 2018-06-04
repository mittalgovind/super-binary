import re

f = open("temp", "r")
l = list(f)

regex = r";; (\d+) succs { ([\d+ ]*) }"
match = re.search(regex, l[-1])
n = int(match.group(1)) + 1

mat = [[0 for i in range(n)] for j in range(n)]

for line in l:
	match = re.search(regex, line)
	i = int(match.group(1))
	js = match.group(2).split(' ')
	for j in js:
		mat[i][int(j)] = 1

print (mat)