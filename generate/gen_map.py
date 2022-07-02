#! /usr/bin/python3


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
for line in open("input.txt","rt"):
    lcnt+=1
    if (lcnt%1000)==0:
        sys.stderr.write("\r"+str(lcnt))
        sys.stderr.flush()
#for line in open("direkt36_post.txt","rt"):
    for w in line.split():
        for c in ',.!?„”‘’“–»«': w=w.replace(c," ") # fixme
        w=w.replace("õ","ő")
        w=unicodedata.normalize('NFKC', w)
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

cnt=0
cnt2=0
wordmap={}
for l in wcount:
    c=wcount[l]
    if c>25:
        cnt+=1
        a=walias[l]
        m=0
        for w in a:
            if a[w]>m: m=a[w]
        m=m//10
        if m<2: m=2
        aa=[]
        for w in a:
            if a[w]>m: aa.append((a[w],w))
        aa.sort(reverse=True)
        if len(aa)>1:
            cnt2+=1
            print(c,l,aa)
            c1,w1=aa[0]
            c2,w2=aa[1]
            wordmap[l]=w1+"|"+w2
        elif len(aa)==1:
            c1,w1=aa[0]  # 110 oszodi [(109, 'őszödi')]
            if w1!=l:
                print(c,l,w1)
                wordmap[l]=w1

print(cnt2,cnt,len(wcount))
pickle.dump(wordmap,open("wordmap.pck","wb"))
