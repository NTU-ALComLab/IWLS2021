import numpy as np
import pickle

def getInd(s):
    ind1=s.find('[')
    ind2=s.find(']')
    return int(s[ind1+1:ind2])

def getXInd(s):
    ind1=s.find('x')
    ind2=s.find(' }')
    return int(s[ind1+1:ind2])

def getShift(s):
    ind1=s.find('<<<')
    if ind1==-1:
        return 0
    else:
        #ind2=s.find('')
        # print(s)
        # print("s:",s[ind1+3:ind2])
        return int(s[ind1+6:ind1+7])

cktFolder="oriCkt"
layerNames=["conv11","conv21","conv22","dense1","dense"]
zeroMats=[np.zeros((640,4*768)),np.zeros((288,4*512)),np.zeros((208,4*384)),np.zeros((20,4*496)),np.zeros((10,4*20))]
#layerNames=["conv11"]
stringRec=dict()
matrices=dict()

for i,layer in enumerate(layerNames):
    stringRec[layer]=[]
    matrices[layer]=zeroMats[i]
    f=open(f"{cktFolder}/{layer}.v",'r')
    lines=f.readlines()
    lInd=0
    while lInd<len(lines):
        l=lines[lInd]
        #print(l)
        if l.find("assign temp_y")!=-1:
            oInd=getInd(l)
            lInd+=1
            l=lines[lInd][1:]
            terms=l.split('+')
            for j,term in enumerate(terms):
                if term.find("-$signed")!=-1:
                    terms[j]=term.split("-$signed")[0]
            stringRec[layer].append(terms)
            print(terms)
            for term in terms:
                if term.find("x")== -1:
                    continue
                print("term: " ,term)
                neg=(term.find("-")!=-1)
                xInd=getXInd(term)
                shift=getShift(term)
                print(neg,xInd,shift,sep=' ')
                matrices[layer][oInd,xInd*4+(4-shift)-1]= -1 if neg else 1
            
        lInd+=1

for i,layer in enumerate(layerNames):
    with open(f"parseRet/{layer}.npy",'wb') as f:
        np.save(f,matrices[layer])