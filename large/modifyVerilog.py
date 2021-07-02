import numpy as np
import pickle
from Covering import Covering

numBits=5

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
        ind2=s.find(' )')
        return int(s[ind1+6:ind2])

def writeSharing(mat,sharedW,unsharedW,file):
    sharingMap=dict()
    for i in range(len(sharedW)):
        file.write(f"wire [13:0] sharing{i};\n")
    for i,cover in enumerate(sharedW):
        file.write(f"assign sharing{i} = ")
        terms=[]
        c_set=cover.c_setPos| cover.c_setNeg
        egRInd=list(cover.r_set)[0]
        for col in c_set:
            xInd=col//numBits
            shift=(numBits-1)-col%numBits
            neg=(mat[egRInd,col]==-1)
            term="$signed("+ ("-{" if neg else "{")
            term+= (f"{shift+1}'b0,x{xInd}" +"}")
            if shift>0:
                term+= f"<<<3'd{shift})"
            else:
                term+=")"
            terms.append(term)
        file.write("+".join(terms)+";\n")

def buildSharingMap(mat,sharedW):
    sharingMap=dict()
    for i,cover in enumerate(sharedW):
        egRInd=list(cover.r_set)[0]
        c_set=cover.c_setPos | cover.c_setNeg
        egCInd=list(c_set)[0]
        for row in cover.r_set:
            if row in sharingMap:
                sharingMap[row].append(f"$signed(sharing{i})" if mat[row][egCInd]==mat[egRInd][egCInd] else f"$signed(-sharing{i})")
            else:
                sharingMap[row]=[f"$signed(sharing{i})" if mat[row][egCInd]==mat[egRInd][egCInd] else f"$signed(-sharing{i})"]
    return sharingMap



cktFolder="oriCkt"
layerNames=["conv11","conv21","conv22","dense1","dense"]
#layerNames=["conv11"]
sharedWs=dict()
unSharedWs=dict()
mats=dict()
sharingMaps=dict()
for l in layerNames:
    sharedWs[l]=pickle.load(open(f"covering/{l}SharedW_3.pkl",'rb'))
    unSharedWs[l]=pickle.load(open(f"covering/{l}UnsharedW_3.pkl",'rb'))
    #mats[l]=np.load(open(f"modified/rec/{l}.npy",'rb'),allow_pickle=True)
    mats[l]=np.load(f"parseRet/{l}.npy",allow_pickle=True)
    for r,row in enumerate(mats[l]):
        for c in np.argwhere(row!=0).squeeze():
            # if l=="conv21" and r==279:
            #     print("c:",c)
            inSomeCover=False
            for cover in sharedWs[l]:
                c_set=cover.c_setNeg|cover.c_setPos
                if c in c_set and r in cover.r_set:
                    inSomeCover=True
                    break
            # if l=="conv21" and r==279:
            #     print("inSome cover:",inSomeCover)
            if not inSomeCover:
                unSharedWs[l][r].add(c)
    #chk covering
    numAllTerm=np.abs(mats[l]).sum(axis=1)
    rec=dict()
    for r in range(mats[l].shape[0]):
        rec[r]=0
    for cover in sharedWs[l]:
        c_set=cover.c_setNeg|cover.c_setPos
        for r in cover.r_set:
            #print("r:",r)
            temp=0
            for c in c_set:
                temp+=1
            rec[r]+=temp
    for r in unSharedWs[l]:
        rec[r]+=len(unSharedWs[l][r])
    for r in range(mats[l].shape[0]):
        #print(l,',',r)
        assert(numAllTerm[r]==rec[r])



for i,layer in enumerate(layerNames):
    fout=open(f"modifiedCkt/{layer}_m.v",'w')
    f=open(f"{cktFolder}/{layer}.v",'r')
    lines=f.readlines()
    lInd=0
    mat=mats[layer]
    sharingMap=buildSharingMap(mat,sharedWs[layer])
    while lInd<len(lines):
        l=lines[lInd]
        #print(l)
        if l==");\n":
            fout.write(l)
            writeSharing(mats[layer],sharedWs[layer],unSharedWs[layer],fout)

        elif l.find("assign temp_y")!=-1:
            oInd=getInd(l)
            fout.write(l)

            lInd+=1
            l=lines[lInd][1:]
            if l.find("-$signed")==-1:
                biasTerm='+'+l.split('+')[-1]
            else:
                #biasTerm=f"$signed(-{l.split('-')[-1][:-2]});\n"
                biasTerm='-'+l.split('-')[-1]
            if oInd==48:
                print("bias term:",biasTerm)
            terms=[]
            
            for col in unSharedWs[layer][oInd]:
                
                xInd=col//numBits
                #print(col,',',xInd)
                
                shift=(numBits-1)-col%numBits
                neg=(mat[oInd,col]==-1)
                term="$signed("+ ("-{" if neg else "{")
                term+= (f"{shift+1}'b0,x{xInd}" +"}")
                if shift>0:
                    term+= f"<<<3'd{shift})"
                else:
                    term+=")"
                terms.append(term)
            
            if oInd in sharingMap:
                terms+=sharingMap[oInd]
            #terms.append(biasTerm)
            fout.write('+'.join(terms))
            fout.write(biasTerm)
        else:
            fout.write(l)
            
        lInd+=1
    fout.close()
    f.close()

# for i,layer in enumerate(layerNames):
#     with open(f"modified/rec/{layer}.npy",'wb') as f:
#         np.save(f,mats[layer])
