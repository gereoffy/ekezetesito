#! /usr/bin/python3

import os
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


wordmap=pickle.load(open("wordmap.pck","rb"))

wcount={}
walias={}
wpairs={}

lcnt=0
skip=0
skip2=0

redlim=5000000
redw=1

redlim2=10000000
redw2=1

for fnev in os.listdir("TXT"):
  print("\n"+fnev)
  for line in open("TXT/"+fnev,"rt",encoding="utf-8",errors="ignore"):
    lcnt+=1
    if (lcnt%1000)==0:
      sys.stderr.write("\r%10d   words=%d  pairs=%d  skip=%d/%d"%(lcnt,len(wcount),len(wpairs),skip,skip2))
      sys.stderr.flush()

      if len(wcount)>redlim:
      # reduce
        d=[]
        for l in wcount:
          if wcount[l]<=redw: d.append(l)
        print("\ndeleting %d words <=%d"%(len(d),redw))
        for l in d:
          del wcount[l]
          del walias[l]
        if len(wcount)>redlim*0.9: redw+=1

      if len(wpairs)>redlim2:
      # reduce
        d=[]
        m=0
        for l in wpairs:
          if wpairs[l]<=redw2: d.append(l)
          elif wpairs[l]>m: m=wpairs[l]
        print("\ndeleting %d pairs <=%d   max=%d"%(len(d),redw2,m))
        for l in d:
          del wpairs[l]
        if len(wpairs)>redlim2*0.8: redw2+=1


    line=unicodedata.normalize('NFC', line)
    line=line.replace("à","á") # ehh
    line=line.replace("è","é") # ehh
    line=line.replace("î","í") # ehh
    line=line.replace("ò","ó") # ehh
    line=line.replace("õ","ő") # ehh
    line=line.replace("ô","ő") # ehh
    line=line.replace("û","ű") # ehh

    try:
        lineb=line.encode('ASCII')
        skip+=1
        continue
    except:
        pass

#    line2=remove_accents(line)
#    if line==line2:
#        skip+=1
#        continue

    for c in '"\',.!?:;/()[]{}„”‘’“–»«':
        if c in line: line=line.replace(c," ") # fixme

    # ekezettel irt?
    ecnt=0
#    wcnt=0
#    line2=[]
    for w in line.lower().split():
#        wcnt+=1
        w=w.strip()
        if w in wordmap:
            if not "|" in wordmap[w]:
                ecnt+=1
#                w="{"+w+"}"
#        line2.append(w)
#    if ecnt>wcnt/5: skip2+=1 # ha a szavak legalabb 5-ode ekezet nelkul van irva...
    if ecnt>=5:  # ha legalabb 5 szo ugy van irva, hogy tudjuk 1:1-ben van ekezetes megfeleloje...
        skip2+=1
#        print(line.strip()[:160])
#        print( (" ".join(line2))[:160] )
        continue

    lastw=None
    for w in line.split():
        w=w.strip().lower()
        if len(w)<2 or len(w)>20: continue
        l=remove_accents(w)
        try:
            wcount[l]+=1
            try:
                walias[l][w]+=1
            except:
                walias[l][w]=1
            # ha ez egy gyakori szo, es az elozo is az, megjegyezzuk a part!
            if wcount[l]>100:
                if lastw:
                  try:
                    wpairs[lastw+"+"+w]+=1
                  except:
                    wpairs[lastw+"+"+w]=1
                lastw=w
            else:
                lastw=None
        except:
            wcount[l]=1
            walias[l]={}
            walias[l][w]=1
            lastw=None

  print("saving...")
  pickle.dump(wcount,open("wcount.pck","wb"))
  pickle.dump(walias,open("walias.pck","wb"))
  pickle.dump(wpairs,open("wpairs.pck","wb"))

sys.stderr.write("reading complete!\n")

