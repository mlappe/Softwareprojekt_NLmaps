python3 ./nmt/translate.py 0
python3 ./nmt/translate.py 1
python3 ./nmt/extractmrls.py
python2 ./Evaluation/evaluate.py ./nmt/nmtout.mrl ./Endcorpus/test.mrl
