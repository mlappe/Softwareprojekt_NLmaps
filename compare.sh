#!/bin/bash

# Das Skript dient dazu, Anfragen an die Datenbank zu stellen 
# und Ergebnisse zu vergleichen.
# Output Codes: 0 - falsche Ausgabe, 1 - OK, 2 - inkorrekte MRL.
# Der Pfad zu der Datenbank (z. 10 und 12) entspricht dem auf ella.
 
echo $1 > sys_mrl.in
echo $2 > gold_mrl.in
/resources/softpro/ss16/nlmaps/overpass-nlmaps/query_db -d /resources/softpro/ss16/nlmaps/db/ -a sys_mrl.out -f sys_mrl.in 2> error
test "$(<error)" != '' && rm sys_mrl.in gold_mrl.in sys_mrl.out error && exit 2
/resources/softpro/ss16/nlmaps/overpass-nlmaps/query_db -d /resources/softpro/ss16/nlmaps/db/ -a gold_mrl.out -f gold_mrl.in
touch comp.out
cmp sys_mrl.out gold_mrl.out > comp.out;
test "$(<comp.out)" == '' && exit 1 || exit 0
rm sys_mrl.in gold_mrl.in sys_mrl.out gold_mrl.out comp.out error
