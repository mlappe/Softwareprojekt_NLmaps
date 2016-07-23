#####################################################################
#																	#
#	Given a Moses n-best output file, the module finds the first	#
#	valid translation if there is one and writes it to a file  		# 
#	or writes an empty line otherwise.								#
#																	#
#	python select_from_nbest.py	moses-nbest-file output-file		#
#																	#
#																	#
#																	#
#####################################################################

import sys
import my_cfg_set as cfg

if __name__ == "__main__":
	lines = open(sys.argv[1],"r").readlines()
	
	n_best = dict() # (Key: sentence number, Value: list of translations)
	for line in lines:
		i, text, rest = line.split("|||",2)
		print (text)
		n_best.setdefault(int(i),[]).append(text.strip())
	print(n_best)
	outfile = open(sys.argv[2], "w")
	
	#set mrl parser
	parser = cfg.EarleyParser()
	grammar_file = "cfg.txt"
	gr = cfg.Grammar(grammar_file)
	parser.set_grammar(gr)
	
	first_line = True
	for candidates in n_best.values():
		if not first_line:
			outfile.write("\n")
		first_line = False
		best_option = " "
		for candidate in candidates:
			bool = parser.parse_mrl(candidate)
			print(candidate, bool)
			if bool:
				best_option = candidate
				break
		outfile.write(best_option)
	outfile.close()