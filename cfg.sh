#!/bin/sh

# run this as ./cfg.sh cfilename
# note that the input needs to be given without the .c extension

gcc $1.c -fno-stack-protector -m32 -static -o $1.out
objdump -S $1.out > $1.S

gcc -S $1.c -fdump-tree-all-graph -fno-stack-protector -m32 -static -o $1.s
dot -Tpng -o $1.png $1.c.011t.cfg.dot
cat $1.c.011t.cfg | grep -E --only-matching 'Function [A-Za-z_0-9]+' > funcs_$1.txt
cat $1.c.011t.cfg | grep -v ';;' | grep -E '[A-Za-z_0-9]+ \(.*\)' > funcprot_$1.txt
python process_funcs.py $1; 
no_of_funcs=`wc -l funcs_$1.txt | grep -oE '[0-9]* '`;

mkdir graphs;
cd graphs ;
for i in `seq 1 $no_of_funcs`; 
do
	touch graph"$i";
	touch addr"$i";
done

cd .. ;
python get_control_graphs.py $1;
cd graphs
touch results;
for graph in graph*;
do
	../dom < $graph >> results
done
mv results ..
cd ..

python getsecpoints.py $1;
gcc -c labelled_$1.s -o $1.o -m32 -g 
gcc -m32 $1.o -o $1.out -g

# cleanup after waiting for other processes to stop
sleep 1;
rm -r graphs ;
rm $1.c.* ;
rm funcs_$1.txt ;
# rm results ;
