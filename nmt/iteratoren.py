mrlfilename = "../Endcorpus/train.mrl"
nlfilename = "../Endcorpus/train.nl"

def traindataiterator():
	with open(mrlfilename) as mrlfile:
		with open(nlfilename) as nlfile:
			for index,mrl in enumerate(mrlfile):
				nl = nlfile.readline()
				yield MRL_Linearizer.linearizeMRL(mrl),MRL_Linearizer.stemNL(nl)
