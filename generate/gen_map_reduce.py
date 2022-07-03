#! /usr/bin/python3


import sys
import pickle


wcount=pickle.load(open("wcount.pck","rb"))
walias=pickle.load(open("walias.pck","rb"))
print(len(wcount))

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
