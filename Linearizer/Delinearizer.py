# This is a module for delinearization of linearized MRLs(Map-Numbers-to-Consonants-Version).
# Contains functions: delinearizer --> Takes linearized MRL as argument, returns delinearized(normal) MRL.
#                     fileReader --> Takes delinearized file and goldstandard MRL file to check delinearization.
#                     fileWriter --> Takes files with linearized MRLs and a target file for the delinearized MRLs as input and generates them.

def delinearizer(LMRL):
    inpt = filter(None,LMRL.split(" "))
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
                ques.append(a)
                stack.append("0")
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
            print("Bad Data")
            blöd += 1
            continue
    return (first_strng.replace("%"," "))

def fileReader(checkfile,goldfile):
    with open(checkfile) as check:
        check_lst = check.readlines()
    with open(goldfile) as gold:
        gold_lst = gold.readlines()
    for index,a in enumerate(check_lst):
        if delinearizer(a).strip() == gold_lst[index].strip().replace("> ",">").replace(" <","<").replace("   "," "):
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
    
        
