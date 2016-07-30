#!/usr/bin/env python3
##################################################
# a short program to clean the corpus, no need to execute again
#by Max Lappé
import os

inputfolder = "./Endcorpus"

is_mrlfile = lambda name: True if name.endswith(".mrl") else False

for dirname,subdirs,filelist in os.walk(inputfolder):
	for fname in filelist:
		if not is_mrlfile(fname):
			continue
		with open(dirname+"/"+fname) as f:
			with open(dirname+"/2"+fname,"w+") as out:
				for line in f:
					print (line)
					line = line.replace("  "," ")
					line = line.replace(" "," ")
					line = line.replace(", ",",")
					line = line.replace("‘","'")
					line = line.replace("’","'")
					out.write(line)
