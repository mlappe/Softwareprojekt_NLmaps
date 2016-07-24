# Noch nicht ganz fertig.... Aufruf: fileWriter(LinearisiertesFile,ZielFile(Delinearisiert))

def delinearizer(LMRL):
    inpt = LMRL.split(" ")
    first_strng = "$"
    stack = []
    ques = []
    no_quot= ["count","latlong","mi","WALKDING_DIST","DIST_OUTTOWN","DIST_INTOWN","DIST_DAYTRIP","km"]
    dic = {"b":"0","c":"1","d":"2","f":"3","g":"4","h":"5","j":"6","k":"7","l":"8","m":"9"}
    blöd = 0
    for index,a in enumerate(inpt):
        try:
            if len(a) == 10 and all(c in dic for c in a):
                stri = ""
                for b in a:
                    stri = stri + dic[b]
                stri = "'<nom>"+stri+"</nom>'"
                first_strng = first_strng.replace("$",stri,1)
            else:    
                que,no = a.split("@")
                stack.append(no[0])
                ques.append(que)
                if no[0] == "s":
                    if que in no_quot or (que.isdigit() and (ques[index-1] == "topx" or ques[index-1] == "maxdist")):
                        first_strng = first_strng.replace("$",que,1)
                    else:
                        first_strng = first_strng.replace("$","'"+que+"'",1)
                if no[0].isdigit() and int(no[0]) > 1:
                    first_strng = first_strng.replace("$",que+"("+"$,"*(int(no[0])-1)+"$"+")",1)
                if no[0].isdigit() and int(no[0]) == 1:
                    first_strng = first_strng.replace("$",que+"("+"$"+")",1)
                if no[0].isdigit() and int(no[0]) == 0: # and int(stack[index-1]) == 0 and que not in no_quot and que.isdigit() == False:
                    if que in no_quot or  (que.isdigit() and (ques[index-1] == "topx" or ques[index-1] == "maxdist")):
                        first_strng = first_strng.replace("$",que,1)
                    else:
                        first_strng = first_strng.replace("$","'"+que+"'",1)
        except ValueError:
            print("Blöde Daten")
            blöd += 1
            continue
    return (first_strng.replace("%"," "))

def fileReader(checkfile,goldfile):
    with open(checkfile) as check:
        check_lst = check.readlines()
    with open(goldfile) as gold:
        gold_lst = gold.readlines()
    for index,a in enumerate(check_lst):
        if delinearizer(a).strip() == gold_lst[index].strip():
            print (True)
        else:
            print (index,False)
            print (delinearizer(a))
            print (gold_lst[index])

def fileWriter(inpt,outpt):
    with open(inpt) as check:
        check_lst = check.readlines()
    with open(outpt,"w") as file:
        for a in check_lst:
            file.write(delinearizer(a)+"\n")
    
        

#fileReader("MRL_EN_TRAIN_YANG_linearizedTEST2.train.LMRL","Downloads/test.mrl")    
#print (fileReader2("Schreibtisch/nlmaps/nlmaps.train.mrl"))
fileWriter("MRL_EN_TRAIN_YANG_linearizedTEST3.train.LMRL","Schreibtisch/Delinearized3.txt")
#print (delinearizer("query@3 area@1 keyval@2 name@0 fjbbhfmmcl nwr@1 keyval@2 name@0 Loreleyhafen@s qtype@1 findkey@1 seamark:harbour:category@0"))
