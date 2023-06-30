#! /usr/bin/python3

import sys
import pickle
import re
import json

wordmap=pickle.load(open("wordpairs.pck","rb"))

tree={}

def treeadd(w,out=None):
  if not out: out=wordmap[w]
  t=tree
  while w:
    c=w[0]
    w=w[1:]
    try:
        t=t[c]
    except:
        t[c]={}
        t=t[c]
  t[0]=out
  return


for w in wordmap: treeadd(w)

#print(tree)
#print(json.dumps(tree,indent=2))

data=bytearray()

def treesize(t):
    n=0
    for c in t:
        if c==0:
            n+=1
            continue
        n+=treesize(t[c])
    return n


def treedict(t,d,base=""):
    for c in t:
        if c==0:
            if base: d[base]=t[c]
        else:
            treedict(t[c],d,base+c)
    return d


def dumptree(t,indent=""):

    global data
    l=len(t)
    p=len(data)

    if 0 in t:
        s=t[0] # integer
        print(indent,p,"int",s)
        if (s&255)==0: data.append(1)
        else: data.append((s)&255)
        data.append(((s>>8)&255))
        data.append(((s>>16)&255))
        data.append(((s>>24)&255))
    else:
        data.append(0)

    p=len(data)

    st=treesize(t)
    print("subtree size:",st)
    if st<16:
        td={}
        treedict(t,td)
        print(len(td),td)
        #
        data.append(len(td))
        data.append(0xFF)
        for w in td:
            print(indent,p,"dict",w,td[w])
            s=w.encode("utf-8")
            data.append(len(s))
            data+=s
            s=td[w] # integer
            data.append(((s)&255))
            data.append(((s>>8)&255))
            data.append(((s>>16)&255))
            data.append(((s>>24)&255))
        return

    data+=b'\x00\x00\x00\x00\x00'*l
    data+=b'\x00\x00'
    for c in t:
        if c==0: continue
        q=len(data)
        print(indent,p,c,q)
        data[p]=ord(c)&255
        data[p+1]=(ord(c)>>8)&15
        data[p+2]=((q)&255)
        data[p+3]=((q>>8)&255)
        data[p+4]=((q>>16)&255)
        data[p+1]|=((q>>24)<<4)
#        data[p+5]=((q>>24)&255)
        p+=5
        dumptree(t[c],indent)


dumptree(tree)
#print(data)

open("wordpairs.dat","wb").write(data)
