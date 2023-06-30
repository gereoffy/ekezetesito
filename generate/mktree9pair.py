#! /usr/bin/python3

import sys
import pickle
import re
import json


# huncode:  0/6/13/14,  0=off,  13=best(1 or 2 bytes),  6=1byte,  14=2bytes
use_huncode=13

# dict: subtree size, 0=off,  8-16=recommended, 10-12=best
use_dict=8

# rle: bits used for RLE code, 0=off, min 2, 4-8 recommended
use_rle=7
rle_mask=((1<<(8-use_rle))-1) # mask for unicode bits  4->15  6->3  0->255



wordmap=pickle.load(open("wordpairs.pck","rb"))

tree={}

def treeadd(w,out=None):
  if not out: out=wordmap[w]

  for c in w:
      if ord(c)>0x1FF:  # non-ascii char in key?
        print(w,out,c)
        return # skip
      if not c in "-+0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzáéíóöőúüű":
        print(w,out,c)
        return # skip

  wc=w
  t=tree
  while wc:
    c=wc[0]
    wc=wc[1:]
    try:
        t=t[c]
    except:
        t[c]={}
        t=t[c]

  t[0]=(w,out)
  return


for w in wordmap: treeadd(w)

#print(tree)
#print(json.dumps(tree,indent=2))

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


def rlecode778(out):
#    for i in range(32):
#        if out<(1<<i): break
#    print("bits",i)
#    return bytes([out&255,(out>>8)&255,(out>>16)&255,out>>24])
    if out<128: return bytes([out]) # 7 bit
    out-=128
    if out<128*128: return bytes([128|(out&127),out>>7]) # 2x7=14 bit
    out-=128*128
    if out>=128*128*256: out=128*128*256-1
    return bytes([128|(out&127),128|((out>>7)&127),out>>14]) # 7+7+8=22 bit

def rlecode678(out):
    if out<64: return bytes([out]) # 6 bit
    out-=64
    if out<64*128: return bytes([64|(out&63),out>>6]) # 6+7=13 bit
    out-=64*128
    if out>=64*128*256: out=64*128*256-1
    return bytes([64|(out&63),128|((out>>6)&127),out>>13]) # 6+7+8=21 bit



def dumptree(t,indent=""):

    data=bytearray()
    l=len(t)
    p=len(data)

    if 0 in t:
#        print(indent,p,"leaf",t[0])
#        s=huncode(t[0][0],t[0][1],True)
        s=rlecode678(t[0][1])
#        data.append(len(s))
        data+=s
#        print(data)
        l-=1
    else:
#        print(indent,p,"0")
        data.append(0)
#    print(l,t.keys())
    p=len(data)

    st=treesize(t)
#    print("subtree size:",st)
    if st<use_dict:
        td={}
        treedict(t,td)
#        print(len(td),td)
        #
#        data.append(len(td))
#        data.append(0xFF)
        data[0]|=128 # dict flag

        for w in td:
#            print(indent,p,"dict",w,td[w])
            s=w.encode("utf-8")
            data.append(len(s))
            data+=s
#            s=td[w].encode("utf-8")
#            s=huncode(td[w][0],td[w][1],False)
            s=rlecode778(td[w][1])

#            data.append(len(s))
            data+=s
        return data

#  26919 RLE 0 4 2
#  32824 RLE 0 8 8
#  33308 RLE 0 7 7
#  34708 RLE 0 9 9
#  45941 RLE 2 2 4 !
#  47294 RLE 2 2 1 !
# 116077 RLE 0 5 5
# 123012 RLE 0 6 6
 
#    data+=b'\x00\x00\x00\x00\x00'*l
#    data+=b'\x00\x00'
    rle_max=(1<<use_rle)-3
    for c in t:
        if c==0: continue
        q=len(data)
#        print(indent,p,c,q)
        #
        d2=dumptree(t[c],indent+"  ")
        dl=len(d2)
        if use_rle==0:
            sl,s=0,bytes([dl&255,(dl>>8)&255,dl>>16]) # 4 bitet meg fel lehetne azert hasznalni?
        elif dl<rle_max: #  253->1byte 254->2byte 255->3byte
            sl,s=dl,b''  # 0-252
        elif dl<(256+rle_max):
            sl,s=rle_max,bytes([dl-rle_max])
        elif dl<65536:
            sl,s=rle_max+1,bytes([dl&255,dl>>8])
        else: #if dl<65536*256:
            sl,s=rle_max+2,bytes([dl&255,(dl>>8)&255,dl>>16])
#        print("RLE",len(s),sl,dl)
        # 10 bit unicode charcode (0x000-0x3ff) + 6 bit RLE block-length code
        data.append(ord(c)&255)
#        data.append(((ord(c)>>8)&3)|(sl<<2))
        if use_rle==8: data.append(sl)
        else: data.append( ((ord(c)>>8)&rle_mask) | (sl<<(8-use_rle)) )
        data+=s
        data+=d2
    return data

    
data=dumptree(tree)
#print(data)

open("wordpairs.dat","wb").write(data)
