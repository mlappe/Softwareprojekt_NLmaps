python3 ./translate.py 0
python3 ./translate.py 1
python3 ./extractmrls.py
python2 ../Evaluation/evaluate.py ../nmt/nmtout.mrl ../Endcorpus/test.mrl
