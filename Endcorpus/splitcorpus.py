import random
mrlfilename = "all.mrl"
nlfilename = "all.nl"
outpath = ""


def corpusiter():
	#iterates over the whole corpus and return nl,mrl	
	with open(mrlfilename) as mrlfile:
		with open(nlfilename) as nlfile:
			for mrl in mrlfile:
				nl = nlfile.readline()
				yield nl, mrl

def create_corpussplit(trainpercentage,tunepercentage,testpercentage):
	assert trainpercentage+tunepercentage+testpercentage > 0.99999
	trainmrlfile = open(outpath+"train.mrl","w+")
	trainnlfile = open(outpath+"train.nl","w+")
	tunemrlfile = open(outpath+"tune.mrl","w+")
	tunenlfile = open(outpath+"tune.nl","w+")
	testmrlfile = open(outpath+"test.mrl","w+")
	testnlfile = open(outpath+"test.nl","w+")

	traincount = 0
	tunecount = 0
	testcount =  0

	for nl,mrl in corpusiter():
		rn = random.random()
		if rn < trainpercentage:
			traincount += 1
			print("train",rn)
			trainmrlfile.write(mrl)
			trainnlfile.write(nl)
		elif rn < tunepercentage+trainpercentage:
			tunecount += 1
			print("tune",rn)
			tunemrlfile.write(mrl)
			tunenlfile.write(nl)
		elif rn < 1.0:
			testcount += 1
			print("test",rn)
			testmrlfile.write(mrl)
			testnlfile.write(nl)
	print("Number of train instances: "+str(traincount))
	print("Number of tune instances: "+str(tunecount))
	print("Number of test instances: "+str(testcount))

if __name__ == "__main__":
	create_corpussplit(0.7,0.2,0.1)
