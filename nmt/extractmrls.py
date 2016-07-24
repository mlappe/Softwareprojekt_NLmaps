with open("mrls.txt") as f:
	with open("out.txt","w+") as out:
		for line in f:
			tokens = line.split("|||")
			out.write(tokens[2].replace("$",""))
