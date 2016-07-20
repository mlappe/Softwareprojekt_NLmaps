# -*- coding: utf-8 -*-

# Scriptname: countertransformer.py
# Author: N.Heinzen
# counts the produced MRL-natural language pairs and transforms them into a useable format

# when calling this method, an input file (MRL-natural language pairs) and an two output files have to be specified

import sys

# writes the results into the specified output file
def writeFile(inputFile, text):
    try:
        file = open(inputFile, 'w+')
        for item in text:
            file.write(item)
        file.close()
    except IOError:
        sys.stderr.write("File could not be written!\n")

# counts the MRL-natural language pairs
def countpairs(inputFile):
    counter= 0
    inFile = open(inputFile, 'r', encoding='utf-8')
    for line in inFile:
        counter+=1
    amount = counter / 2
    print(amount)
    inFile.close()

# transforms the MRL-natural language pairs in a useable format (two text documents)
def transformpairs(inputFile):
    inFile = open(inputFile, 'r', encoding='utf-8')
    outputFile1 = sys.argv[2]
    outputFile2 = sys.argv[3]
    mrlNaturalPairs = {}
    prevLine = ""
    for line in inFile:
        if line.replace("\n", "").endswith(")"):
            mrlNaturalPairs[prevline] = line
        prevline = line
    writeFile(outputFile1, mrlNaturalPairs.keys())
    writeFile(outputFile2, mrlNaturalPairs.values())

inputFile = sys.argv[1]
transformpairs(inputFile)
countpairs(inputFile)
