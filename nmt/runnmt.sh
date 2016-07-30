python3 ./translate.py --maxSteps 1600 --size 256 --num_layers 3 --learning_rate 0.5
python3 ./translate.py --decode --beam 100
python2 ../Evaluation/evaluator.py ../nmt/nmtout.mrl ../Endcorpus/test.mrl
