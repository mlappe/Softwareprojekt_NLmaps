import MRL_Linearizer,sys

#################################################################################################################################################
#                                                                                                                                               #
# Autor: Ozan Yilmaz                                                                                                                            #
#                                                                                                                                               #
# Dies ist das LinearizedMrlFileCreater-Modul für das Softwareprojekt Semantic Parsing as Monolingual Machine Translation.                      #
#                                                                                                                                               #
# Enthält folgende Funktionen:                                                                                                                  #
#                                                                                                                                               #
# 1) linearizedFileCreater(txt) -->  Erstellt ein File mit linearisierten MRLS, gegeben das .txt-file mit MRLs                                  #
#                                                                                                                                               #
# 2) stemmedFileCreater -->   Erstellt ein File mit gestemmten natürlichsprachlichen Anfrangen, gegeben .txt-file mit NL-Anfragen               #                                                                                                           #
#                                                                                                                                               #
#################################################################################################################################################

def LinearizedFileCreater(txt):
    with open(txt) as myfile:
        txt_lst = myfile.readlines()
    new_txtlst = []
    for a in txt_lst:
        sentence = []
        for b in range(len(a)):
            if  a[b-1].isalpha() and a[b] == "'" and a[b+1].isalpha():
                sentence.append(a[b].replace("'",""))
            else:
                sentence.append(a[b])
        new_txtlst.append("".join(sentence).strip())
        
    with open('MRL_EN_TEST_linearized.txt','w') as newfile:
        for a in new_txtlst:
            newfile.write(MRL_Linearizer.linearizeMRL(a)+"\n")
    



def stemmedFileCreater(txt):
    with open(txt) as myfile:
        txt_lst = myfile.readlines()
        
    with open('NL_EN_TEST_stem.txt','w') as newfile:
        for a in txt_lst:
            newfile.write(MRL_Linearizer.stemNL(a)+"\n")


if __name__ == "__main__":
    LinearizedFileCreater("MRL_train.txt")
    stemmedFileCreater("NL_en_training.txt")

