#! /usr/bin/python3

import sys
import pickle
import re
import json


# huncode:  0/6/13/14,  0=off,  13=best(1 or 2 bytes),  6=1byte,  14=2bytes
use_huncode=13

# dict: subtree size, 0=off,  8-16=recommended, 10-12=best
use_dict=10

# rle: bits used for RLE code, 0=off, min 2, 4-8 recommended
use_rle=8
rle_mask=((1<<(8-use_rle))-1) # mask for unicode bits  4->15  6->3  0->255



wordmap=pickle.load(open("wordmap.pck","rb"))

tree={}

def treeadd(w,out=None):
  if not out: out=wordmap[w]
  if len(out)>=64: # max 127 lehet, mivel a legfolso bit a DICT flag!
    print(w,out)
    crash()
  os=out.split("|")
  for o in os:
    if len(w)!=len(o) or len(w)>=32:
#      print(w,out,o)
      return # skip
    for c in w:
      if ord(c)>127:  # non-ascii char in key?
        print(w,out,o,c)
        return # skip
    for c in o:
      if not c in "-0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzáéíóöőúüű":
#        print(w,out,o)
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

  bits=0
  for o in os:
    for i in range(len(w)):
      c=w[i]
      if c in "aei": bits+=1
      elif c in "ou": bits+=2
  ob=b'\xFF'*((bits+7)>>3)

  # 1. byte:  n e llllll    n=1 akkor 2 szo van, a hosszt (l) duplazni kell!  ha e=0 akkor l hosszu utf8

#  print(bits,len(ob),len(out),ob,out)

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


def huncode(w,out,leaf):
    os=out.split("|")
    ob=out.encode("utf-8")
    ob=bytes([len(ob)])+ob

    if (len(os)>1 and leaf) or not use_huncode or len(os)>2: return ob

    data=0
    bits=0
    for o in os:
      if len(w)!=len(o): return ob # can't encode
      for i in range(len(w)):
        c=w[i]
        d=o[i]
        if d in "aáeéiíoóöőuúüű":
            # encode bits
            if c in "aei":
                if c!=d: data|=1<<bits
                bits+=1
            elif c in "ou":
                data|=("oóöőuúüű".find(d)&3)<<bits
                bits+=2
            else: crash()  #WTF
            if bits>use_huncode:
#                print("too much bits",bits,w,out)
                return ob
        elif c!=d: return ob # can't encode special char!

    if use_huncode==13:
      if bits<=5:
        ob=bytes([0x40 | (128*(len(os)-1)) | (data&31)]) # 5 bits
      else:
        ob=bytes([0x60 | (128*(len(os)-1)) | (data&31) ,data>>5]) # 5+8=13 bits
    elif use_huncode==14:
      ob=bytes([0x40 | (128*(len(os)-1)) | (data&63) ,data>>6]) # 6+8=14 bits
    elif use_huncode==6:
      ob=bytes([0x40 | (0x80*(len(os)-1)) | (data&63)]) # 6 bits

#    print(bits,out,bin(ob[0]),bin(ob[0]))
    return ob

def dumptree(t,indent=""):

    data=bytearray()
    l=len(t)
    p=len(data)

    if 0 in t:
#        print(indent,p,"leaf",t[0])
        s=huncode(t[0][0],t[0][1],True)
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
            s=huncode(td[w][0],td[w][1],False)
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

open("wordmap.dat","wb").write(data)
