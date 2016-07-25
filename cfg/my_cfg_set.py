import re,sys,os

class Grammar:
	
	def __init__(self, grammarfile = os.path.abspath(os.path.join(os.path.dirname( __file__ ), './cfg.txt'))):
		self.rules = dict()
		self.start_symbol = "[S]"
		self.nonterminals = set([])
		
		if grammarfile:
			self.read_rules(grammarfile)
			##print self.rules["[S]"]
			##print self.nonterminals
		
	def read_rules(self, grammarfile):
		rules = dict()
		with open(grammarfile) as rule_file:
			#list [[LHS, RHS], [LHS2, RHS2], ...], wobei LHS sich wiederholen koennen
			list_rules = [[elem.strip() for elem in rule.split("|||")] for rule in rule_file.readlines() ]
			##print(list_rules[:5])
			for rule in list_rules:
				##print "\nStart adding a rule:"
				lhs, rhs = rule
				##print "lhs:" + lhs
				rhs_splitted = [RHS_elem.strip() for RHS_elem in rhs.split()]
				##print "rhs: ", rhs_splitted
				##print "dict: ", rules
				default = rules.setdefault(lhs,[])
				##print "default: ", default
				##print "dict: ", rules
				##print "old value: ", rules[lhs]
				##print "new value: ", [].append(5555)
				default.append(rhs_splitted)
				##print "new value: ", rules[lhs]
				##print "dict: ", rules
				self.nonterminals.add(lhs)	
		self.rules = rules

class Edge:

	def __init__(self, first, last, head, elements,  seen , pos = 0):
		self.first = first
		self.last = last
		self.head = head
		self.elements = elements
		self.pos = pos
		self.seen = seen
	
	def icr_pos(self):
		self.pos += 1
		
	def __str__(self):
		return str(self.first) + " " + str(self.last) + " " + self.head + str(self.elements) + " " + str(self.pos)
		

def check_parent(string):
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
			#print string, i
			return string[opening:i]
	return ""
	
def find_val(string, list):
	#if len(string.split()) == 1:
	#	list.append(string.strip())
	#	return 
	#print "try to find a value in ", string
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
		#TO DO: ersetzen beliebige Werte durch 'valvariable'
		if not check_parent(mrl):
			return False
		mrl = mrl.replace(" ","").replace(")"," ) ").replace("(", "( ").replace("'", " ' ").replace(",", " , ")
			
		#print mrl
		k = re.compile("keyval\(  ' .*? '  , ")
		match_iter = k.finditer(mrl)
		replace_list = []
		#print "i found matches" , match_iter
		for match_obj in match_iter:
			#print "i have a match!"
			start = match_obj.start()
			keyval = find_parent(mrl[start:])
			#print keyval
			try:			
				find_val(find_parent(mrl[start:]).split(",")[1] , replace_list)
			except:
				#print "no comma found"
				return ""
			
		for val in replace_list:
			#print "replace value: ", val
			mrl = mrl.replace(val, "valvariable")
		return mrl.split()
		
			   
	def expand_for(self, nonterm, pos):
		new_edges = []
		for expansion in self.grammar.rules[nonterm]:
			new_edges.append(Edge(pos, pos, nonterm, expansion, []))
		return new_edges
		
		
	def parse_mrl(self, mrl):
		if "$" in mrl:
			return False
		gr = self.grammar
		start = gr.start_symbol
		self.edges = set([])
		self.built_phrases = dict()
		old_edges = set([])
		
		mrl = self.preprocess_mrl(mrl)
		mrl_pos = 0
		#print "parsing: " , mrl
		#initialize starting rules
		self.edges = self.edges.union(set(self.expand_for(start, 0)))
		to_check = set(self.edges)
		 
		go_ahead = True
		while (go_ahead)and(mrl_pos < len(mrl)):  
			go_ahead = False
			##print "EXPAND"
			#expand		
			depth = 0 
			#print "check"
			while to_check and (depth < self.exp_depth):
				new = [] 
				depth += 1
				for e in to_check:
					##print "checking edge", e
					if e.pos < len(e.elements):
						##print "checking head", e.elements[e.pos]
						if e.elements[e.pos] in gr.nonterminals:
							new += self.expand_for(e.elements[e.pos], e.last)
							self.edges = self.edges.union(set(new))
				##print new
				to_check = set(new)
				##print(to_check)
			##print ("HI!")				
			if old_edges != self.edges:
				go_ahead = True
				old_edges = self.edges
				
			#for e in self.edges:
			#	#print e
			
			to_check = set([])
			
			##print("MATCH")
			#match-
			next_word = mrl[mrl_pos]
			##print "checking word %s"%next_word
			for e in self.edges:
				#if e.head != "[KEY]":
				#	#print "match ", next_word, "in ", e 
				if e.pos < len(e.elements):
					if (next_word == e.elements[e.pos])and(mrl_pos == e.last ):
						e.last += 1
						e.pos += 1
						to_check.add(e)
						go_ahead = True
						
						#print "matched: ", next_word, "in ", e
			mrl_pos += 1
			##print mrl_pos
			if not go_ahead:
				#print "could not match the word:", next_word, "at ", mrl_pos
				#for i in self.edges:
					#if i.pos != 0:
						#print i
				#print self.built_phrases
				return False
				

			#for e in self.edges:
			#	#print e
			
			cont = True
			while cont:			
				cont = False
				##print("FINISH RULES")
				#find passive edges
				edges = self.edges.copy()
				for e in edges:
					if e.pos == len(e.elements):
						self.built_phrases.setdefault((e.first,e.last), []).append(e.head)
						#print "i built " , e
						self.edges.remove(e)
						#delete completed phrases from self.edges ???		

				#shift
				##print("SHIFTING IN THE RULES")
				edges = self.edges.copy()
				for e in edges:
					#if ((e.first,e.last) == (13,15)) and (e.head == "[INNER]"):
						#print "trying to find ", e.elements[e.pos], "in ", e
					for first, last in self.built_phrases:
						#if ((e.first,e.last) == (13,15)) and (e.head == "[INNER]"):
							#print e.seen
						if (e.last == first) and (e.elements[e.pos] in self.built_phrases[(first,last)]) and ((first, last) not in e.seen):
							e.seen.append((first,last))
							shifted_rule = Edge(e.first, last, e.head, e.elements, [], e.pos +1)
							self.edges.add(shifted_rule)
							#print "shifted over ", self.built_phrases[(first,last)], "in ", e
							#if ((e.first,e.last) == (13,15)) and (e.head == "[INNER]"):
								#print e.seen
							#e.last = last
							#e.pos += 1
							to_check.add(shifted_rule)
							cont = True		
							go_ahead = True
			##print to_check == False
			#for e in to_check:
			#	#print e
			#for e in self.edges:
			#	#print e
			
			#go_ahead = False
		#find_parses
		
		#for p in self.built_phrases:
		#	print p, self.built_phrases[p], "sh"
			
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
	
	#print mrl2
	#print "The MRL is", output	

	