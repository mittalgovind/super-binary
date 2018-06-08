#!/bin/sh

# run this as ./cfg.sh cfilename
# note that the input needs to be given without the .c extension
gcc $1.c -fdump-tree-all-graph -o $1.out
objdump -S $1.out > $1.s
dot -Tpng -o $1.png $1.c.011t.cfg.dot

cat $1.c.011t.cfg | grep -E --only-matching '\([A-Za-z_0-9]+,' > funcs_$1.txt
touch $1.S
python makematrix.py $1
# ./dom < graph


# cat $1.011t.cfg | grep -F ';;' > temp
# rm temp
# rm $1.*
# gdb ./boost_1_67_0/dom
# rm graph