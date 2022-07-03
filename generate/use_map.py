#! /usr/bin/python3

import sys
import pickle

confusables={}

def load_unicodes(fnev):
    # try to load unicodes.map from file
    for line in io.open(fnev,"rt",encoding="utf-8",errors="ignore"):
        l=line.rstrip("\n\r").split("\t",1)
        confusables[ord(l[0])]=l[1]
#    print("%d entries loaded from %s file" %(len(confusables),fnev))

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
#            print("%d entries generated from unicodedata.normalize" %(len(confusables)))
    return "".join(confusables.get(ord(x),"") if ord(x)>=128 else x for x in input_str)

# elés tészt lész
wordmap=pickle.load(open("wordmap.pck","rb"))
#print(wordmap["eles"])
#print(wordmap["teszt"])
#print(wordmap["lesz"])

#fo=open("test.out","wt")
for line in sys.stdin: #open("test.txt","rt"):
    newline=[]
    for w in line.split():
        nw=w
        for c in '-,.!?:;/()[]{}„”‘’“–»«': w=w.replace(c," ") # fixme
        w=w.replace("õ","ő")
        w=unicodedata.normalize('NFKC', w)
        if not w or len(w)<2:
            newline.append(nw)
            continue
        l=w.strip().lower()
        if l in wordmap:
            if l in nw:
                nw=nw.replace(l,wordmap[l])
            elif l in nw.lower():
                nw=nw.lower().replace(l,wordmap[l])
            else:
                nw=w.replace(l,wordmap[l])
        newline.append(nw)
    #fo.write(" ".join(newline)+"\n")
    #fo.flush()
    print(" ".join(newline))
