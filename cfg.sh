#!/bin/sh

# run this as ./cfg.sh cfilename
# note that the input needs to be given without the .c extension

python insert_verification_code.py $1 ;
gcc $1_injected.c -fno-stack-protector -m32 -static -o $1_injected.out ;
objdump -S $1_injected.out > $1_injected.S ;
gcc -S $1_injected.c -fdump-tree-all-graph -fno-stack-protector -m32 -static -o $1_injected.s ;
dot -Tpng -o $1_injected.png $1_injected.c.011t.cfg.dot ;
cat $1_injected.c.011t.cfg | grep -E --only-matching 'Function [A-Za-z_0-9]+' > funcs_$1_injected.txt ;
cat $1_injected.c.011t.cfg | grep -v ';;' | grep -E '[A-Za-z_0-9]+ \(.*\)' > funcprot_$1_injected.txt ;
python process_funcs.py $1_injected ; 
no_of_funcs=`wc -l funcs_$1_injected.txt | grep -oE '[0-9]* '` ;

mkdir graphs ;
cd graphs ;
for i in `seq 1 $no_of_funcs` ; 
do
	touch graph"$i" ;
	touch addr"$i" ;
done

cd .. ;
python get_control_graphs.py $1_injected ;
cd graphs
touch results;
for graph in graph*;
do
	../dom < $graph >> results
done
mv results ..
cd ..

python getsecpoints.py $1_injected ;
python insert_labels.py $1_injected ;
python generate_verification_graph.py $1_injected ;
sleep 1;
gcc -c labelled_$1_injected.s -o $1_injected.o -m32 -g -static -fno-stack-protector;
gcc -m32 $1_injected.o -o $1_injected.out -g -static -fno-stack-protector;
touch verify_$1_injected.txt
echo '' > verify_$1_injected.txt
# to be removed 
# ./$1_injected.out  
# cleanup after waiting for other processes to stop
python monitor.py $1_injected
sleep 1;
rm -r graphs ;
rm $1_injected.c.* ;
rm funcs_$1_injected.txt ;
rm results ;
rm funcprot_$1_injected.txt;
# rm labelled_$1_injected.s $1_injected.o
# rm processed_funcs_$1_injected.txt
rm $1_injected.s $1_injected.S