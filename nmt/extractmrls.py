with open("out.txt") as f:
	with open("nmtout.mrl","w+") as out:
		for line in f:
			tokens = line.split("|||")
			out.write(tokens[2].replace("$",""))
