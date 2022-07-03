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
wpairs=pickle.load(open("wordpairs.pck","rb"))
#print(wordmap["eles"])
#print(wordmap["teszt"])
#print(wordmap["lesz"])

#fo=open("test.out","wt")
lastword="NoNe"
for line in sys.stdin: #open("test.txt","rt"):
    newline=[]
    for w in line.split():
        nw=w
        for c in ',.!?:;/()[]{}„”‘’“–»«': w=w.replace(c," ") # fixme
        w=w.replace("õ","ő")
        w=unicodedata.normalize('NFKC', w)
        if not w or len(w)<2:
            newline.append(nw)
            continue
        l=w.strip().lower()
        if l in wordmap:
            uj=wordmap[l]
            try:
                w1,w2=uj.split("|")
                try:
                    pc1=wpairs[lastword+"+"+w1]
                except:
                    pc1=2
                try:
                    pc2=wpairs[lastword+"+"+w2]
                except:
                    pc2=1
                if pc1>10*pc2:
                    uj="+"+w1
                elif pc2>10*pc1:
                    uj="++"+w2
                elif pc2>pc1:
                    uj=w2+"|"+w1 # sokkal valoszinubb a 2. alak...
            except:
                pass
            if l in nw:
                nw=nw.replace(l,uj)
            elif l in nw.lower():
                nw=nw.lower().replace(l,uj)
            else:
                nw=w.replace(l,uj)
            lastword=uj
        else:
            lastword=l
        newline.append(nw)
    #fo.write(" ".join(newline)+"\n")
    #fo.flush()
    print(" ".join(newline))
