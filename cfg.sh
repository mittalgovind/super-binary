#!/bin/sh

gcc $1 -fdump-tree-all-graph
dot -Tpng -o $1.png $1.011t.cfg.dot
cat $1.011t.cfg | grep succs > temp
python makematrix.py
rm temp
