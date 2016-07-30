import MRL_Linearizer,sys

######################################################################################################################################################
#                                                                                                                                                    #
# Author: Ozan Yilmaz                                                                                                                                #
#                                                                                                                                                    #
# This is the LinearizedMrlFileCreater module(Map-numbers-to-consonants) for the softwareprojekt Semantic Parsing as Monolingual Machine Translation.#
#                                                                                                                                                    #
# Contains following functions:                                                                                                                      #
#                                                                                                                                                    #
# 1) linearizedFileCreater(txt) -->  Creates a file with linearized MRLS, given file with MRLs                                                       #
#                                                                                                                                                    #
# 2) stemmedFileCreater -->   Creates file with stemmed NL Questions, given file with NL-Questions               #                                   #
#                                                                                                                                                    #
######################################################################################################################################################

def LinearizedFileCreater(txt):
    lst = ["-",":","&","."]
    dic = {"b":"0","c":"1","d":"2","f":"3","g":"4","h":"5","j":"6","k":"7","l":"8","m":"9"}

    with open(txt) as myfile:
        txt_lst = myfile.readlines()
    new_txtlst = []
    for a in txt_lst:
        sentence = []
        for b in range(len(a)):
            if  a[b-1].isalpha() and a[b] == "'" and a[b+1].isalpha():
                sentence.append(a[b].replace("'","§"))
            else:
                sentence.append(a[b])
        new_txtlst.append("".join(sentence).strip())
        
    with open('MRL_EN_TRAIN_YANG_linearizedTEST3.train.LMRL','w') as newfile:
        for a in new_txtlst:
            s = MRL_Linearizer.linearizeMRL(a).replace("§","'")
            finish = []
            for b in range(len(s)):
                if s[b] == " " and (s[b-1].isalpha() or s[b-1] in lst) and s[b-2] != "@":
                    appender = s[b].replace(" ","%")
                    finish.append(appender)
                else:
                    finish.append(s[b])
            newfile.write(("".join(finish)+"\n").replace("% "," "))
    



def stemmedFileCreater(txt):
    with open(txt) as myfile:
        txt_lst = myfile.readlines()
        
    with open('Schreibtisch/progTest2/tune.nl','w') as newfile:
        for a in txt_lst:
            newfile.write(MRL_Linearizer.stemNL(a)+"\n")


if __name__ == "__main__":
    #LinearizedFileCreater("Downloads/Softwareprojekt_NLmaps-master/Endcorpus/train.mrl")
    #stemmedFileCreater("Schreibtisch/progTest2/corps/tune.nl")

