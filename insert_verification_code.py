import sys

source = open(sys.argv[1] + '.c', 'r')
source = list(source)
verify_method_code = "\nFILE* verify_me_please;\n\n" \
				+ "int init_file_for_vErIfY(){\n\tverify_me_please = fopen(\"verify_" + sys.argv[1] +".txt\", \"rw+\");\n}\n\n" \
				+ "int vErIfY(char name[100]){\n\tfprintf(verify_me_please, \"%s\\n\", name);\n}\n"
flag = 0 
header = False
dest = []
insert_pos = -1 
for i, line in enumerate(source):
	if '#' in line :
		if "stdio" in line:
			header = True
		insert_pos = i + 1
		continue
# this header is needed for our verification code to run
if insert_pos == -1:
	insert_pos = 0

if header == False: 
	source.insert(0, "#include <stdio.h>")
	insert_pos += 1

sink = open(sys.argv[1]+'_injected.c', 'w')

for i in range(insert_pos):
	sink.write(source[i])

sink.write(verify_method_code)
for i in range(insert_pos, len(source)):
	sink.write(source[i])

sink.close()