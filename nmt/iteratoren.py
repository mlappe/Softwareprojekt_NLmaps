mrlfilename = "../Endcorpus/train.mrl"
nlfilename = "../Endcorpus/train.nl"

def traindataiterator():
	with open(mrlfilename) as mrlfile:
		with open(nlfilename) as nlfile:
			for index,mrl in enumerate(mrlfile):
				nl = nlfile.readline()
				yield mrl,nl
