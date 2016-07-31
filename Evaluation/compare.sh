#!/bin/bash

# This script evaluates two MRLs against the database.
# The path to the database is that on the CL servers.
# Output codes: 0 - wrong output, 1 - OK, 2 - incorrect MRL.
 
echo $1 > sys_mrl.in
echo $2 > gold_mrl.in
/resources/softpro/ss16/nlmaps/overpass-nlmaps/query_db -d /resources/softpro/ss16/nlmaps/db/ -a sys_mrl.out -f sys_mrl.in 2> error
test "$(<error)" != '' && rm sys_mrl.in gold_mrl.in sys_mrl.out error && exit 2
/resources/softpro/ss16/nlmaps/overpass-nlmaps/query_db -d /resources/softpro/ss16/nlmaps/db/ -a gold_mrl.out -f gold_mrl.in
touch comp.out
cmp sys_mrl.out gold_mrl.out > comp.out;
rm sys_mrl.in gold_mrl.in sys_mrl.out gold_mrl.out error
test "$(<comp.out)" == '' && rm comp.out && exit 1 || rm comp.out || exit 0
