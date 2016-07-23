#!/usr/bin/python                                                 
#-*- coding: UTF-8 -*-  

######################################################################
#                                                                    #
#                                                                    #
#  Dieses Modul dient zur Evaluation der erzeugten MRLs.             #
#  Dazu werden die Ergebnisse einer Anfrage mit den Ergebnissen      #
#  der Gold-Anfrage verglichen und die Accuracy berechnet.           #
#  Somit werden mur zwei Anfragen mit 100 Prozent                    #
#  identischen Ausgaben als gleiche bewertet.                        #
#                                                                    #
#  ZU BEACHTEN:                                                      #
#  1. Die Datei "compare.sh" muss sich in demselben Ordner befinden. #
#  2. Das Skript funktioniert sowohl in Python2 als auch in Python3. #
#  3. Die Input-Dateien müssen jeweils eine MRL pro Zeile enthalten  #
#    und gleich lang sein.                                           #
#                                                                    #
#  Um die Evaluation durchzuführen, braucht man folgenden Befehl:    #
#                                                                    #
#     python2 evaluator.py system_mrl_file gold_mrl_file             #
#                                                                    #
#  Recall is defined as the percentage of correct answers out of	 #
# all examples, Precision the percentage of correct answers out of	 #
# all examples with an answer, and F1-score the harmonic mean		 #
# between the two aforementioned.	(Carolin Haas)					 #
#  																	 #
#                                                                    #
#  Autor:  Marina Speranskaya                                        #
#                                                                    #
######################################################################

import subprocess, sys


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
		for i,mrl in enumerate(mrl_list):
			sys_mrl = '"'+mrl+'"'
			gold_mrl = '"'+gold_mrl_list[i]+'"'
			command = "bash ./compare.sh %s %s"%(sys_mrl,gold_mrl)
			result = subprocess.call(command,shell=True)
			self.result_list.append(result)
			if i%10 == 0:
				sys.stdout.write("%d out of %d completed\n"%(i,len(mrl_list)))
		return
		
	def calc_acc(self):
		tp = 0
		incorrect = 0 
		#inc_list = []
		for (pos,value) in enumerate(self.result_list):
			if value ==1:
				tp += 1
			elif value ==0:
				pass
			else:
				incorrect += 1
				#inc_list.append(pos)
		if incorrect:
			sys.stdout.write("There were %d incorrect system MRLs.\n"%incorrect)
			#print (inc_list)
		#print(tp)
		self.recall = float(tp) / len(self.result_list)
		self.precision = float(tp) / (len(self.result_list) - incorrect)
		if self.precision + self.recall != 0:
			self.fscore = (2*self.recall*self.precision)/(self.recall+self.precision)
		else: 
			self.fscore = 0
		return
	
if __name__ == "__main__":
	ev = Evaluator(sys.argv[1],sys.argv[2])
	ev.compare_queries()
	ev.calc_acc()
	print ("Recall: %f Precision: %f \nF1-Score: %f"%(ev.recall,ev.precision,ev.fscore))
	