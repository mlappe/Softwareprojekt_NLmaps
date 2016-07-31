This is a short description for running our SMT model and installing Moses

First of all, follow the instructions in this video to install moses properly and colloquate all the files in the correct folders:

https://www.youtube.com/watch?v=aaalgJoRy54

OR

ALL NECESSARY COMMANDS:

*** Installing MOSES Decoder ***

Install required pacakages : sudo apt-get install g++ git automake libtool zlib1g-dev libboost-all-dev libbz2-dev liblzma-dev libgoogle-perftools-dev

Clone Moses from Github :
git clone https://github.com/moses-smt/mosesdecoder

Download & Install GIZA++ git clone https://github.com/moses-smt/giza-pp.git cd giza-pp make

Copying GIZA++ Binaries to MosesDecoder: cd ~/mosesdecoder mkdir tools cp ~/giza-pp/GIZA++-v2/GIZA++ ~/giza-pp/GIZA++-v2/snt2cooc.out ~/giza-pp/mkcls-v2/mkcls tools

Install Moses
./bjam
(NOTE : This may take a lot of time! )

###################################################################################

Eventually, create a folder containing a folder "corps" with six files: train.nl/mrl, test.nl/mrl and tune.nl/mrl [just unzip corps.zip or look at Linearized_Stemmed_Corpora]
and "mosespipe.sh"(mosespipe should be in the main folder, not in "corps"). The folder should also contain following:

select_from_nbest.py,my_cfg_set.py,Delinearizer.py(num-to-consonant-version),cfg.txt and (if you want to clear the folder fast again) clear.sh.

Look at MosesFolder1.png and Mosesfolder2.png to see how it's meant to be.

Now you should be able to run mosespipe.sh.

"listfile" contains the n-best translations
"outputOfTest.txt" contains the resulting translations

Our final output, which is ready for evaluation, is called "bestofList".

Endresult of mosespipe.sh in folder should look like this: MosesFolder3.png 

For the Evaluation you need to make use of the Evaluation folder and Evaluator.py, which needs to be run on ella (Database is installed on Ella, but not mosesdecoder, that's why you need to do this step seperately).

Example for Evaluating: MosesFolder4.png [test-eval.mrl is provided in Evaluation folder and can be used]

For Evaluation you need to have bestofList and the unlinearized test.mrl [!NOTE: corps contains the linearized version!]
Than you can get the Precision,Recall and F1-Score with following command:

python3 evaluator.py bestofList test.mrl

You can use clear.sh to delete everything created by mosespipe.sh, if you want to start a new run.

NOTE: In general, Machine Translation training is non-convex. this means that there are multiple solutions and each time you run a full training job, you will get different results. It is recommended to do some runs (let's say 10) and calculate the average fscore.
