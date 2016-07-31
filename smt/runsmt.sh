#!/bin/bash

bash mosespipe.sh
python3 select_from_nbest.py outputOfTest.txt smtout.mrl > record
python2 ../Evaluation/evaluator.py smtout.mrl ../Endcorpus/test.mrl