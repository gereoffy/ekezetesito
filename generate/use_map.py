#! /usr/bin/python3

import sys
import pickle
import re

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

    # fix unicode 
    line=unicodedata.normalize('NFC', line)
    line=line.replace("à","á") # ehh
    line=line.replace("è","é") # ehh
    line=line.replace("î","í") # ehh
    line=line.replace("ò","ó") # ehh
    line=line.replace("õ","ő") # ehh
    line=line.replace("ô","ő") # ehh
    line=line.replace("û","ű") # ehh

    def isalpha(c):
        if c in "-_0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz": return True
        if c in ',.!?:;/()[]{}„”‘’“–»«': return False
        return ord(c)>=128

    newline=""
    p=0
    while p<len(line):

      # skip whitespace
      while p<len(line):
        c=line[p]
#        for c in ',.!?:;/()[]{}„”‘’“–»«': w=w.replace(c," ") # fixme
        if isalpha(c): break
        p+=1
        newline+=c

#      print(p)
#      print(newline)
      
      if line[p:p+7] in ["http://","https:/"]:
        # skip url
        q=p
        while p<len(line) and not line[p] in "\"'] \t\n": p+=1
#        print("URL: "+line[q:p])
        newline+=line[q:p]
        continue

      # read next word:
      w=""
      while p<len(line):
        c=line[p]
        if not isalpha(c): break
        p+=1
        w+=c

#      print(p)
#      print(w)

#      print(p,newline,w)
#      break

      if not w or len(w)<2:
        newline+=w
      else:
        # process word:

        if w[0]=='-':
          newline+=w[0]
          w=w[1:]

        ws=w.split("-")
        nw2=[]

        for w in ws if len(ws)==2 and (not ws[1] or len(ws[1])>=5) else [w]:
#          print(w)
          nw=w
          l=w.lower()

          if l and l in wordmap:
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
                    uj=w1
                elif pc2>10*pc1:
                    uj=w2
                elif pc2>pc1:
                    uj=w2+"|"+w1 # sokkal valoszinubb a 2. alak...
            except:
                pass
            lastword=uj
            if l==w: nw=uj
            elif l.upper()==w: nw=uj.upper()
            else: nw=uj[0].upper()+uj[1:] # capitalise hack
          else:
            lastword=l
          nw2.append(nw)

        newline+="-".join(nw2)

    #fo.write(" ".join(newline)+"\n")
    #fo.flush()

    print(newline,end='')
