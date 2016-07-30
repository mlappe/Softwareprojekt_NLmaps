# -*- coding: utf-8 -*-
from nltk.stem.porter import *
import nltk,shlex

#################################################################################################################################################
#                                                                                                                                               #
# Author: Ozan Yilmaz                                                                                                                           #
#                                                                                                                                               #
# This is the MRL_Linearizer module(Map-numbers-to-consonants for the softwareprojekt Semantic Parsing as Monolingual Machine Translation.      #
#                                                                                                                                               #
# Contains following functions:                                                                                                                 #
#                                                                                                                                               #
# 1) linearizeMRL(MRL) --> returns linearized form                                                                                              #
#                                                                                                                                               #
#    Example: linearizeMRL("query(area(keyval(name,'Paris')), nwr(keyval(tourism,'hotel'),keyval(wheelchair,'yes')),find-key(name)))")          #
#                                                                                                                                               #
#    Return: query@3 area@1 keyval@2 name@0 Paris@s nwr@2 keyval@2 tourism@0 hotel@s keyval@2 wheelchair@0 yes@s find-key@1 name@0              #
#                                                                                                                                               #
# 2) stemNL(nl) --> returns stemmed verions of question without question mark.                                                                  #
#                                                                                                                                               #
#    Example: stemNL("Which hotels in Paris have wheelchair access?")                                                                           #
#                                                                                                                                               #
#    Return: Which hotel in Pari have wheelchair access                                                                                         #
#                                                                                                                                               #
#################################################################################################################################################

def tokenizerMRL(MRL):
    return shlex.split(" ".join(nltk.word_tokenize(MRL)))

def linearizeMRL(MRL):
    MRL_tokenized = tokenizerMRL(MRL)
    linearized_list = []
    for a in enumerate(MRL_tokenized):
        if a[1] != "(" and a[1] != ")" and a[1] != ",":
            bracket_counter = 0
            arg_counter = 0
            for b in enumerate(MRL_tokenized):
                if b[0] > a[0]:
                    if b[1] == "(":
                        bracket_counter += 1
                    if b[1] == ")":
                        bracket_counter -= 1
                    if b[1] == "," and bracket_counter == 1:
                        arg_counter += 1
                    if b[1] == ")" and bracket_counter == 0:
                        arg_counter += 1
                        linearized_list.append(a[1].strip().replace(" ","")+"@"+str(arg_counter))
                        break
                    if b[1] == "," and bracket_counter == 0:
                        linearized_list.append(a[1].strip().replace(" ","")+"@"+str(arg_counter))
                        break
                    if b[1] == ")" and bracket_counter == -1 and MRL_tokenized[b[0]-2] == ",":
                        linearized_list.append(a[1].strip()+"@"+"s")
                        break
                    if b[1] == ")" and bracket_counter == -1 and MRL_tokenized[b[0]-2] == "(":
                        linearized_list.append(a[1].strip().replace(" ","")+"@"+str(arg_counter))
                        break
                    else:
                        continue
        else:
            continue
    foreal = []
    dic = {"0":"b","1":"c","2":"d","3":"f","4":"g","5":"h","6":"j","7":"k","8":"l","9":"m"}
    for a in range(len(linearized_list)):
        if "(" in linearized_list[a] and ")" in linearized_list[a]:
            normal,problem = linearized_list[a].split(" ",1)
            foreal.append(normal.strip()+" "+problem.replace(" ",""))
        elif ":" in linearized_list[a]:
            count = 0
            for b in linearized_list[a]:
                if b == ":":
                    count += 1
                else:
                    continue
            if count == 1:
                normal,problem = linearized_list[a].split(":")
                foreal.append(normal.strip()+":"+problem.replace(" ",""))
            elif count > 1:
                foreal.append(linearized_list[a].replace(" ",""))
        elif "." in linearized_list[a]:
            normal,problem = linearized_list[a].split(".")
            foreal.append(normal.strip()+". "+problem.replace(" ",""))
        elif "<" in linearized_list[a] and ">" in linearized_list[a]:
            nom = linearized_list[a].replace(" ","").replace("<nom>","").replace("</nom>","").replace("@s","")
            stri = ""
            for b in nom:
                stri = stri+dic[b]
            foreal.append(stri+" ")       
        else:
            foreal.append(linearized_list[a])
    return " ".join(foreal).strip()

def stemNL(nl):
    stemmer = PorterStemmer()
    stemmed = []
    for a in nltk.word_tokenize(nl.replace("?","").replace("!","")):
        stemmed.append(stemmer.stem(a))

    return " ".join(stemmed).strip() 



