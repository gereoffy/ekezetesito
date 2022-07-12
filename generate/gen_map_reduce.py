#! /usr/bin/python3


import sys
import pickle


try:
    import hunspell
    hobj = hunspell.HunSpell('/usr/share/hunspell/hu_HU.dic', '/usr/share/hunspell/hu_HU.aff')
except:
    hobj=None
    print("Hunspell lib/pip/dict not found!")


wcount=pickle.load(open("wcount.pck","rb"))
walias=pickle.load(open("walias.pck","rb"))
wpairs=pickle.load(open("wpairs.pck","rb"))
print(len(wcount),len(wpairs))
#print(wcount["nelkulihez"],walias["nelkulihez"])
print(wcount["meg"],walias["meg"])

pairs={}

for l in wpairs:
    w1,w2=l.split("+",1)
    c=wpairs[l]
    try:
        pairs[w2][w1]=c
    except:
        pairs[w2]={}
        pairs[w2][w1]=c
del wpairs
wpairs={}

#for l in wcount:
#    c=wcount[l]
#    a=walias[l]
#    aa=[]
#    for w in a: aa.append((a[w],w))
#    aa.sort(reverse=True)
#    print(c,l,aa)
#exit()

def get_pairs(l1,l2):
    aa=[]
    try:
      a=pairs[l1]
      for w in a: aa.append((a[w],w+"+"+l1))
    except:
      pass
    try:
      a=pairs[l2]
      for w in a: aa.append((a[w],w+"+"+l2))
    except:
      pass
    aa.sort(reverse=True)
    bb=[]
    for c,w in aa:
#        bb.append("%s+%s(%d)"%(w,l,c))
#        if c<50: break
        bb.append(w)
        wpairs[w]=c
    return " ".join(bb[:50])

cnt=0
cnt2=0
wordmap={}
for l in wcount:
    c=wcount[l]
    if c>=5:
        cnt+=1
        a=walias[l]
        m=0
        for w in a:
            if a[w]>m: m=a[w]
        m=m//20
        if m<2: m=2
        aa=[]
        for w in a:
            if a[w]>m: aa.append((a[w],w))
        aa.sort(reverse=True)
        if len(aa)>1:
            cnt2+=1
            c1,w1=aa[0]
            c2,w2=aa[1]

            # ha a 2. alak nem tul gyakori, akkor megnezzuk helyesirasellenorzovel :)
            if c1>3*c2 and hobj and not ( hobj.spell(w2) or hobj.spell(w2[0].upper()+w2[1:]) ):
                print("Hunspell:",w2,c1,c2)
                if w1!=l:
                    print(c,l,w1)
                    wordmap[l]=w1
            else:
                print(c,l,aa,get_pairs(w1,w2))
                wordmap[l]=w1+"|"+w2

        elif len(aa)==1:
            c1,w1=aa[0]  # 110 oszodi [(109, 'őszödi')]
            if w1!=l:
                print(c,l,w1)
                wordmap[l]=w1


print(cnt2,cnt,len(wcount))
pickle.dump(wordmap,open("wordmap.pck","wb"))
pickle.dump(wpairs,open("wordpairs.pck","wb"))
