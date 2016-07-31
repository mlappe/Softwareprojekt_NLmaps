#!/usr/bin/python                                                 
#-*- coding: UTF-8 -*-  

######################################################################
#                                                                    #
#  This module serves the evaluation of the produced MRLs.           #
#  The database respond to the system mrl is compared to the		 #
#  gold respond. Only indentical match is considered correct. 		 #
#  																     #
#  For exact definition of used evaluation metrics see the           #
#  presentation slides.												 #
#																	 #
#  IMPORTANT:                                                        #
#  1. The file "compare.sh" must be in the same folder.				 #
#  2. This script can be used in both Python2 and Python3.			 #
#  3. The input files must contain the same amount of MRLs and       #
# 			have one MRL per line.									 #
#                                                                    #
#  For starting the evaluation the following is needed:			     #
#                                                                    #
#     python2 evaluator.py system_mrl_file gold_mrl_file             #
#                                                                    #
#  The output will be displayed in the shell.                        #
#                                                                    #
#  Autor:  Marina Speranskaya                                        #
#                                                                    #
######################################################################

import subprocess, sys, os


class Evaluator:
	
	def __init__(self, sysfile, goldfile):
		self.system_mrl_file = sysfile
		self.gold_mrl_file = goldfile
		self.result_list = []
		self.recall = 0
		self.precision = 0
		self.fscore = 0
		
	def set_system_file(self,filename):
		self.system_mrl_file = filename
	
	def set_gold_file(self, filename):
		self.gold_mrl_file = filename
		
	def compare_queries(self):
		mrl_list = open(self.system_mrl_file).readlines()
		gold_mrl_list = open(self.gold_mrl_file).readlines()
		path_to_comp = os.path.abspath(os.path.join(os.path.dirname( __file__ ), 'compare.sh'))
		for i,mrl in enumerate(mrl_list):
			sys_mrl = '"'+mrl+'"'
			gold_mrl = '"'+gold_mrl_list[i]+'"'
			command = "bash %s %s %s"%(path_to_comp,sys_mrl,gold_mrl)
			result = subprocess.call(command,shell=True)
			self.result_list.append(result)
			if i%10 == 0:
				sys.stdout.write("%d out of %d completed\n"%(i,len(mrl_list)))
		return
		
	def calc_acc(self):
		tp = 0
		incorrect = 0 
		empty = 0 
		for (pos,value) in enumerate(self.result_list):
			if value == 1:
				tp += 1
			elif value == 2:
				incorrect += 1
			elif value == 3:
				tp += 1
				empty += 1
		if incorrect:
			sys.stdout.write("There were %d incorrect system MRLs.\n"%incorrect)
		self.recall = float(tp) / len(self.result_list)
		self.precision = float(tp) / (len(self.result_list) - incorrect)
		if self.precision + self.recall != 0:
			self.fscore = (2*self.recall*self.precision)/(self.recall+self.precision)
		else: 
			self.fscore = 0
		if tp != 0:
			self.e = float(empty) / tp
		else:
			self.e = -1
		return
	
if __name__ == "__main__":
	ev = Evaluator(sys.argv[1],sys.argv[2])
	ev.compare_queries()
	ev.calc_acc()
	print ("Recall: %f Precision: %f \nF1-Score: %f"%(ev.recall,ev.precision,ev.fscore))
	#print(ev.result_list)