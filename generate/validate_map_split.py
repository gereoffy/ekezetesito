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
#wpairs={}
print(len(wordmap),len(wpairs))

#print(wordmap["eles"])
#print(wordmap["teszt"])
#print(wordmap["lesz"])

cnt_all=0
cnt_alt1=0
cnt_alt2=0
cnt_alter=0
cnt_found=0
cnt_good1=0
cnt_bad1=0
cnt_gooda1=0
cnt_gooda2=0
cnt_bada=0
cnt_goodp1=0
cnt_goodp2=0
cnt_badp=0
cnt_notfound=0
cnt_same=0
cnt_split=0

#fo=open("test.out","wt")
lastword="NoNe"
for line in open("test.txt","rt"):

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

        nw=w
        l=remove_accents(w).lower()

        w=w.lower()
        lwiter=[(l,w)]
        ws=w.split("-")
        if not l in wordmap and len(ws)>1 and len(ws[1])>3:
            lwiter=zip(l.split("-"),ws)
            cnt_split+=1
            if l!=w: print(w)
#            print(list(lwiter))

        for l,w in lwiter:

          cnt_all+=1
          if l in wordmap:
            cnt_found+=1
            uj=wordmap[l]
            try:
                w1,w2=uj.split("|")
                cnt_alter+=1
                try:
                    pc1=wpairs[lastword+"+"+w1]
                except:
                    pc1=2
                try:
                    pc2=wpairs[lastword+"+"+w2]
                except:
                    pc2=1
                if pc1>10*pc2:
                    cnt_alt1+=1
                    if w==w1: cnt_goodp1+=1
                    else: cnt_badp+=1
                    uj=w1
                elif pc2>10*pc1:
                    cnt_alt2+=1
                    if w==w2: cnt_goodp2+=1
                    else: cnt_badp+=1
                    uj=w2
                elif pc2>pc1:
                    uj=w2+"|"+w1 # sokkal valoszinubb a 2. alak...
                    if w==w2: cnt_gooda1+=1
                    elif w==w1: cnt_gooda2+=1
                    else: cnt_bada+=1
                else:
                    if w==w1: cnt_gooda1+=1
                    elif w==w2: cnt_gooda2+=1
                    else: cnt_bada+=1
            except:
                if w==uj: cnt_good1+=1
                else: cnt_bad1+=1
#                pass
            if l in nw:
                nw=nw.replace(l,uj)
            elif l in nw.lower():
                nw=nw.lower().replace(l,uj)
            else:
                nw=w.replace(l,uj)
            lastword=uj
          else:
            cnt_notfound+=1
            if l==w: cnt_same+=1
#            else: print(nw,w)
            lastword=l

        newline+=nw
    #fo.write(" ".join(newline)+"\n")
    #fo.flush()
#    print(" ".join(newline))


cnt_good=cnt_good1+cnt_gooda1+cnt_gooda2+cnt_goodp1+cnt_goodp2
print("Counters:  ALL=%d  found=%d (%d multi)  good=%d  same=%d  notfound=%d  split=%d"%(cnt_all,cnt_found,cnt_alter,cnt_good,cnt_same,cnt_notfound,cnt_split))

# Counters:  ALL=249405  found=128124 (14808 multi)  good=127086  same=117573  notfound=121281
#print("Stats:  good: %d of %d found,  rate: %5.3f %%"%(cnt_good,cnt_found,100.0*cnt_good/cnt_found))

print("Hits:  1:1=%d (bad:%d)  pair:%d/%d (bad:%d)  alternatives:%d/%d (bad:%d)"%(cnt_good1,cnt_bad1,  cnt_goodp1,cnt_goodp2,cnt_badp,  cnt_gooda1,cnt_gooda2,cnt_bada))


print("Stats:      found: %d  good: %d  bad: %d = %5.3f %%"%(cnt_found,cnt_good,cnt_found-cnt_good,100.0*(cnt_found-cnt_good)/cnt_found))
print("Stats:  not found: %d  same: %d  bad: %d = %5.3f %%"%(cnt_notfound,cnt_same,cnt_notfound-cnt_same,100.0*(cnt_notfound-cnt_same)/cnt_notfound))
print("Total:  %5.3f %%"%( 100.0*(cnt_good+cnt_same)/cnt_all))



