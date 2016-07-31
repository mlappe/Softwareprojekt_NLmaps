#!/usr/bin/python                                                 
#-*- coding: UTF-8 -*-  

#################################################################
#																#
#	This script implements a parser, that can check if an MRL	#
#	is formed according the given rules.						#
#	The rules are extracted from a file "cfg.txt" which must 	#
#	appear in the same folder.									#
#																#
#	To begin you need to set up the parser:						#
#																#
#	import my_cfg_set as cfg									#
#	parser = cfg.EarleyParser()									#
#																#
#	grammar_file = "cfg.txt"									#
#	gr = cfg.Grammar(grammar_file) 								#
#	parser.set_grammar(gr)										#
#																#
#	output = parser.parse_mrl(mrl)								#
#																#
#	Afterwards, the variable output contains the truth value 	#
#	returned by the method. For more see the demo() function	#
#	at the very end of the script.								#
#																#
#	Autor: Marina Speranskaya									#
#																#
#################################################################

import re,sys,os

class Grammar:
	
	def __init__(self, grammarfile = os.path.abspath(os.path.join(os.path.dirname( __file__ ), './cfg.txt'))):
		self.rules = dict()
		self.start_symbol = "[S]"
		self.nonterminals = set([])
		
		if grammarfile:
			self.read_rules(grammarfile)
		
	def read_rules(self, grammarfile):
		rules = dict()
		with open(grammarfile) as rule_file:
			#list [[LHS, RHS], [LHS2, RHS2], ...], wobei LHS sich wiederholen koennen
			list_rules = [[elem.strip() for elem in rule.split("|||")] for rule in rule_file.readlines() ]
			for rule in list_rules:
				lhs, rhs = rule
				rhs_splitted = [RHS_elem.strip() for RHS_elem in rhs.split()]
				default = rules.setdefault(lhs,[])
				default.append(rhs_splitted)
				self.nonterminals.add(lhs)	
		self.rules = rules

class Edge:

	def __init__(self, first, last, head, elements,  seen , pos = 0):
		self.first = first 	#position of the first token 
		self.last = last 	#current position of the last token
		self.head = head	#left hand side of the rule
		self.elements = elements	#right hand side of a rule
		self.pos = pos		#current position in the rule (the dot)
		self.seen = seen	#list of phrases already used in shifting 
	
	def icr_pos(self):
		self.pos += 1
		
	def __str__(self):
		return str(self.first) + " " + str(self.last) + " " + self.head + str(self.elements) + " " + str(self.pos)
		

def check_parent(string):
	#checks the correctness of parenthesis 
	count = 0
	ok = True
	for c in string:
		if c == "(":
			count += 1
		if c == ")":
			count -= 1
		if count < 0:
			ok = False 
			break
	return ok

def find_parent(string):
	#finds the first upper-level argument surrounded by paranthesis in the given string
	#>>> find_parent("nwr(keyval('name','Burg Eltz'))") 
	#keyval('name','Burg Eltz')
	count = 0
	one = False
	opening = 0
	for i,c in enumerate(string):
		if c == "(":
			if one == False:
				opening = i+1
			one = True
			count += 1
		if c == ")":
			count -= 1
		if (count == 0)and one:
			##print string, i
			return string[opening:i]
	return ""
	
def find_val(string, list):
	#finds all words in value position to be replace later
	#a string with only combinations of values is expected
	words = [word.strip() for word in string.split()]
	for word in words:
		if word not in ["or(", "and(", "(", ")", ",", "'"]:
			list.append(word)
	
class EarleyParser:
		
	def __init__(self):
		self.grammar = Grammar() 
		self.edges = set([])
		self.built_phrases = dict()
		self.exp_depth = 5

	def load_grammar(self, grammarfile):
		self.grammar.read_rules(grammarfile)
	
	def set_grammar(self, grammar):
		self.grammar = grammar
		
	def preprocess_mrl(self,mrl):
		#converts an mrl to a parsable format
		#replaces all values with a space-holder and splits the mrl to cfg specific tokens 
		#In [11]: parser.preprocess_mrl("query(nwr(keyval('amenity','postbox')),qtype(latlong(topx(1))))")
		#Out[11]:['query(', 'nwr(', 'keyval(', "'", 'amenity', "'", ',', "'", 'valvariable', "'", ')', ')', ',', 'qtype(', 'latlong(', 'topx(', '1', ')', ')', ')', ')']
		
		if not check_parent(mrl):
			return False
		mrl = mrl.replace(" ","").replace(")"," ) ").replace("(", "( ").replace("'", " ' ").replace(",", " , ")
				
		k = re.compile("keyval\(  ' .*? '  , ")
		match_iter = k.finditer(mrl)
		replace_values = []
		replace_keys = []
		for match_obj in match_iter:
			start = match_obj.start()
			keyval = find_parent(mrl[start:])
			bevore = mrl[:start]
			try:		
				key, val = keyval.split(",",1)
				find_val(val, replace_values)
			except:
				return []
		
		for val in replace_values:
			mrl = mrl.replace(val, "valvariable",1)
		return mrl.split()
		
			   
	def expand_for(self, nonterm, pos):
		#adds new possible edges for the current active nonterminal
		new_edges = []
		for expansion in self.grammar.rules[nonterm]:
			new_edges.append(Edge(pos, pos, nonterm, expansion, []))
		return new_edges
		
		
	def parse_mrl(self, mrl):
		#the central function for checking the mrl
		
		if "$" in mrl:	#filter wrong delinearised mrls
			return False
			
		gr = self.grammar
		start = gr.start_symbol
		self.edges = set([])
		self.built_phrases = dict()
		old_edges = set([])
		
		mrl = self.preprocess_mrl(mrl)
		mrl_pos = 0
		
		#initialize starting rules
		self.edges = self.edges.union(set(self.expand_for(start, 0)))
		to_check = set(self.edges)
		 
		go_ahead = True #if the next word was matched
		while (go_ahead)and(mrl_pos < len(mrl)):  
			go_ahead = False
			#expand		
			depth = 0 
			while to_check and (depth < self.exp_depth):
				new = [] 
				depth += 1
				for e in to_check:
					if e.pos < len(e.elements):
						if e.elements[e.pos] in gr.nonterminals:
							new += self.expand_for(e.elements[e.pos], e.last)
							self.edges = self.edges.union(set(new))
				to_check = set(new)
			if old_edges != self.edges:
				go_ahead = True
				old_edges = self.edges
			
			to_check = set([])
			
			next_word = mrl[mrl_pos]
			for e in self.edges:
				if e.pos < len(e.elements):
					if (next_word == e.elements[e.pos])and(mrl_pos == e.last ):
						e.last += 1
						e.pos += 1
						to_check.add(e)
						go_ahead = True
			mrl_pos += 1
			
			if not go_ahead:
				return False
			
			cont = True #if new edges were added to check in the next shift iteration
			while cont:			
				cont = False
				#find passive edges
				edges = self.edges.copy()
				for e in edges:
					if e.pos == len(e.elements):
						self.built_phrases.setdefault((e.first,e.last), []).append(e.head)
						self.edges.remove(e)

				#shift
				edges = self.edges.copy()
				for e in edges:
					for first, last in self.built_phrases:
						if (e.last == first) and (e.elements[e.pos] in self.built_phrases[(first,last)]) and ((first, last) not in e.seen):
							e.seen.append((first,last))
							shifted_rule = Edge(e.first, last, e.head, e.elements, [], e.pos +1)
							self.edges.add(shifted_rule)
							to_check.add(shifted_rule)
							cont = True		
							go_ahead = True
				
		if (0, len(mrl)) in self.built_phrases:
			if start in self.built_phrases[(0,len(mrl))]:
				return True

		return False
	
def demo():
	parser = EarleyParser()
	
	grammar_file = "cfg.txt"
	gr = Grammar(grammar_file)
	parser.set_grammar(gr)

	mrl = "dist(query(around(center(area(keyval('name','Paris'),keyval('is_in:country','France')),nwr(keyval('name','Rue Lauriston'))),search(nwr(keyval('shop','bakery'))),maxdist(DIST_INTOWN)),qtype(latlong(topx(1)))),for('car'))"
	mrl2 = "query(area(keyval('name','San Francisco')),nwr(keyval('highway','bus_stop')),qtype(count))"
	output = parser.parse_mrl(mrl2)
	
	print (mrl2)
	print ("The MRL is", output)	

	