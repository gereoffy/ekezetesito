#! /usr/bin/python3

import os
import sys
import pickle

confusables={}

def load_unicodes(fnev):
    # try to load unicodes.map from file
    for line in io.open(fnev,"rt",encoding="utf-8",errors="ignore"):
        l=line.rstrip("\n\r").split("\t",1)
        confusables[ord(l[0])]=l[1]
    print("%d entries loaded from %s file" %(len(confusables),fnev))

import unicodedata

def remove_accents(input_str):
    if len(confusables)==0:
        try:
            load_unicodes("unicodes.map")
        except:
            # generate it with normalize() (without confusables...)
            for ic in range(128,0x20000):
                nfkd_form = unicodedata.normalize('NFKD', chr(ic))
                oc=nfkd_form.encode('ASCII', 'ignore').decode('ASCII', 'ignore')
                if (oc and oc!=chr(ic) and oc!="()"):
                    confusables[ic]=oc
            confusables[215]='x'
            confusables[216]='O' # athuzott 'O' betu
            confusables[248]='o' # athuzott 'o' betu
            confusables[223]='ss' # nemet
            print("%d entries generated from unicodedata.normalize" %(len(confusables)))
    return "".join(confusables.get(ord(x),"") if ord(x)>=128 else x for x in input_str)


wcount={}
walias={}

lcnt=0
skip=0

for fnev in os.listdir("TXT"):
  print("\n"+fnev)
  for line in open("TXT/"+fnev,"rt",encoding="utf-8",errors="ignore"):
    lcnt+=1
    if (lcnt%1000)==0:
        sys.stderr.write("\r%10d   words=%d  skip=%d"%(lcnt,len(wcount),skip))
        sys.stderr.flush()

    line=unicodedata.normalize('NFC', line)
    line=line.replace("à","á") # ehh
    line=line.replace("è","é") # ehh
    line=line.replace("î","í") # ehh
    line=line.replace("ò","ó") # ehh
    line=line.replace("õ","ő") # ehh
    line=line.replace("ô","ő") # ehh
    line=line.replace("û","ű") # ehh

    try:
        lineb=line.encode('ASCII')
        skip+=1
        continue
    except:
        pass

#    line2=remove_accents(line)
#    if line==line2:
#        skip+=1
#        continue

    for c in '"\',.!?:;/()[]{}„”‘’“–»«':
        if c in line: line=line.replace(c," ") # fixme

    for w in line.split():
        w=w.strip().lower()
        if len(w)<2: continue
        l=remove_accents(w)
        try:
            wcount[l]+=1
            try:
                walias[l][w]+=1
            except:
                walias[l][w]=1
        except:
            wcount[l]=1
            walias[l]={}
            walias[l][w]=1

  pickle.dump(wcount,open("wcount.pck","wb"))
  pickle.dump(walias,open("walias.pck","wb"))

sys.stderr.write("reading complete!\n")


