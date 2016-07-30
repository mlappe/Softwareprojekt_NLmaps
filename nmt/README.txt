this is the nmt part of our project

to run it use 
	sh runnmt.sh 
in this folder
the script will train a new model and evaluate it on the test set

the output can be found in 
	./nmt/nmtout.mrl
		contains just the system mrls
	./nmt/out.txt
		contains the decoding step, linearized mrl and mrl


if you want to execute the program manually
	translate.py --maxSteps 1600 --size 256 --num_layers 3 --learning_rate 0.5
		trains a new model 
			size: number of cells in a layer
			num_layers: number of layers
			maxSteps: number of trainig steps
		before execution you have to delete the tmp(with all model data) directory, we did not automate this because we
		want to make sure the deletion is intentional

	translate.py --decode --beam 100
			translates the test data

	translate.py --decode --demo
			start interactive translation
			will prompt you to give a sentence to translate

for more command line options see translate.py



authors:
Max Lappé
Stoyan Dimitrov
