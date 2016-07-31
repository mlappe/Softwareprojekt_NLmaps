# This is a module for delinearization of linearized MRLs(NMT-Version).
# Contains functions: delinearizer --> Takes linearized MRL as argument, returns delinearized(normal) MRL.
#                     fileReader --> Takes delinearized file and goldstandard MRL file to check delinearization.
#                     fileWriter --> Takes files with linearized MRLs and a target file for the delinearized MRLs as input and generates them.

def delinearizer(LMRL):
    inpt = LMRL.split(" ")
    first_strng = "$"
    stack = []
    ques = []
    no_quot= ["count","latlong","mi","WALKDING_DIST","DIST_OUTTOWN","DIST_INTOWN","DIST_DAYTRIP","km"]
    blöd = 0
    for index,a in enumerate(inpt):
        try:
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
    
        

#fileReader("MRL_EN_TRAIN_YANG_linearizedTEST1.train.LMRL","Schreibtisch/nlmaps/nlmaps.train.mrl")    
#print (fileReader2("Schreibtisch/nlmaps/nlmaps.train.mrl"))
#print (delinearizer("query@2 around@4 center@2 area@1 keyval@2 name@0 City%of%Edinburgh@s nwr@1 keyval@2 name@0 Edinburgh%Waverley@s search@1 nwr@1 keyval@2 amenity@0 drinking_water@s maxdist@1 DIST_INTOWN@0 topx@1 1@0 qtype@1 latlong@0"))
#fileWriter("MRL_EN_TRAIN_YANG_linearized.train.LMRL","Schreibtisch/Delinearized.txt")
