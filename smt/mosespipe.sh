# THIS IS A PIPELINE FOR TRAINING AND TESTING OF A STATISTICAL MACHINE TRANSLATION SYSTEM BASED ON MOSES
# This pipeline needs to be in the folder where the output should come out(in this case progTest2), just like the select_from_nbest.py.
# The corpora should be in a subfolder called 'corps' of that folder.
# You need moses and all it's dependencies installed (look at http://www.statmt.org/moses/), and moses accessable from the root directory(~/mosesdecoder/...)
# Also you should have GIZA++ with all it's necessary dependencies installed in ~/mosesdecoder/tools
# Just change the paths below and start.
# You can turn tuning on or off by setting TUNING=true or false. -> If false, Tune sets are not used. 
# NOTE: MRL-FILES should already be linearized with the num-to-consonants version of Linearizer.
# NOTE2: In general, Machine Translation training is non-convex. this means that there are multiple solutions and each time you run a full training job,
# you will get different results.

#Relative path to folder with Corpus and pipeline script:
BASIC_PATH_RELATIVE="~/Schreibtisch/progTest2/"
#Absolute path to folder with Corpus and pipeline script:
BASIC_PATH_ABSOLUTE="/home/ozan/Schreibtisch/progTest2/"

TUNING=true

TRAIN_INPUTLANG="corps/train.nl"

TRAIN_OUTPUTLANG="corps/train.mrl"

TEST_INPUTLANG="corps/test.nl"

TEST_OUTPUTLANG="corps/test.mrl"

TUNE_INPUTLANG="corps/tune.nl"

TUNE_OUTPUTLANG="corps/tune.mrl"

################################################################

mkdir $BASIC_PATH_ABSOLUTE"lm"

~/mosesdecoder/bin/lmplz --o 3 < $BASIC_PATH_ABSOLUTE$TRAIN_OUTPUTLANG  >>  $BASIC_PATH_ABSOLUTE"lm"/train.arpa.mrl --discount_fallback

~/mosesdecoder/bin/build_binary $BASIC_PATH_ABSOLUTE"lm"/train.arpa.mrl $BASIC_PATH_ABSOLUTE"lm"/train.blm.en

nohup nice ~/mosesdecoder/scripts/training/train-model.perl -root-dir $BASIC_PATH_ABSOLUTE"train" -corpus corps/train -f nl -e mrl -alignment grow-diag-final-and -reordering msd-bidirectional-fe -lm 0:3:$BASIC_PATH_ABSOLUTE/lm/train.blm.en:8 -external-bin-dir ~/mosesdecoder/tools >& $BASIC_PATH_RELATIVE/training.out &

wait

if [ $TUNING ]
	then
		nohup nice ~/mosesdecoder/scripts/training/mert-moses.pl $BASIC_PATH_ABSOLUTE$TUNE_INPUTLANG $BASIC_PATH_ABSOLUTE$TUNE_OUTPUTLANG ~/mosesdecoder/bin/moses train/model/moses.ini --mertdir ~/mosesdecoder/bin/ &> $BASIC_PATH_ABSOLUTE"mert.out" &
		wait
		#add/remove parameters ("-n-best-list listfile" for n-best translations, "50 distinct" for 50 different translations
		~/mosesdecoder/bin/moses -f mert-work/moses.ini -n-best-list listfile 50 distinct < $BASIC_PATH_ABSOLUTE$TEST_INPUTLANG > outputOfTest.txt

else
		#add/remove parameters ("-n-best-list listfile" for n-best translations, "50 distinct" for 50 different translations
		~/mosesdecoder/bin/moses -f train/model/moses.ini -n-best-list listfile 50 distinct < $BASIC_PATH_ABSOLUTE$TEST_INPUTLANG > outputOfTest.txt


fi

~/mosesdecoder/scripts/generic/multi-bleu.perl $TEST_OUTPUTLANG < outputOfTest.txt 

python3 select_from_nbest.py listfile bestofList

#python3 evaluator.py bestofList $TEST_OUTPUTLANG
