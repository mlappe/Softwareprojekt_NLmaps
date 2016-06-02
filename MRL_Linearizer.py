# -*- coding: utf-8 -*-
from nltk.stem.porter import *
import nltk

#################################################################################################################################################
#                                                                                                                                               #
# Autor: Ozan Yilmaz                                                                                                                            #
#                                                                                                                                               #
# Dies ist das MRL_Linearizer-Modul für das Softwareprojekt Semantic Parsing as Monolingual Machine Translation.                                #
#                                                                                                                                               #
# Enthält folgende Funktionen:                                                                                                                  #
#                                                                                                                                               #
# 1) linearizeMRL(MRL) --> returniert linearisierte Form                                                                                        #
#                                                                                                                                               #
#    Beispielaufruf: linearizeMRL("query(area(keyval(name,'Paris')), nwr(keyval(tourism,'hotel'),keyval(wheelchair,'yes')),find-key(name)))")   #
#                                                                                                                                               #
#    Return: query@3 area@1 keyval@2 name@0 Paris@s nwr@2 keyval@2 tourism@0 hotel@s keyval@2 wheelchair@0 yes@s find-key@1 name@0              #
#                                                                                                                                               #
# 2) stemNL(nl) --> returniert gestemmte Version der Frage ohne Fragezeichen.                                                                   #
#                                                                                                                                               #
#    Beispielaufruf: stemNL("Which hotels in Paris have wheelchair access?")                                                                    #
#                                                                                                                                               #
#    Return: Which hotel in Pari have wheelchair access                                                                                         #
#                                                                                                                                               #
#################################################################################################################################################

def linearizeMRL(MRL):
    MRL_tokenized = nltk.word_tokenize(MRL.replace("'","").replace(":","_")
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
                        linearized_list.append(a[1]+"@"+str(arg_counter))
                        break
                    if b[1] == "," and bracket_counter == 0:
                        linearized_list.append(a[1]+"@"+str(arg_counter))
                        break
                    if b[1] == ")" and bracket_counter == -1 and MRL_tokenized[b[0]-2] == ",":
                        linearized_list.append(a[1]+"@"+"s")
                        break
                    if b[1] == ")" and bracket_counter == -1 and MRL_tokenized[b[0]-2] == "(":
                        linearized_list.append(a[1]+"@"+str(arg_counter))
                        break
                    else:
                        continue
        else:
            continue
    return " ".join(linearized_list).strip()

def stemNL(nl):
    stemmer = PorterStemmer()
    stemmed = []
    for a in nltk.word_tokenize(nl.replace("?","")):
        stemmed.append(stemmer.stem(a))

    return " ".join(stemmed).strip() 
    
    
                        


