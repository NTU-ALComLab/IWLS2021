# -*- coding: utf-8 -*-
import numpy as np
#import torch
import networkx as nx
import pickle
import math

def generateW(m,n):
    result=np.zeros((m,n),dtype=np.int8)
    for i in range(m):
        for j in range(n):
            r=np.random.randint(0,1001)
            if r%2==0:
                result[i][j]=0
            else:
                result[i][j]=1
    return result

class Covering():
    def __init__(self,rows,colsPos=None,colsNeg=None,bp=8):
        self.rows=rows
        if colsPos!=None:
            self.colsPos=colsPos
            self.c_setPos=set(colsPos)
        else:
            self.c_setPos=self._getCols(pos=True)
            self.colsPos=list(self.c_setPos)
        if colsNeg!=None:
            self.colsNeg=colsNeg
            self.c_setNeg=set(colsNeg)
        else:
            self.c_setNeg=self._getCols(pos=False)
            self.colsNeg=list(self.c_setNeg)
        self.bp=bp
        self.r_set=set(rows)
        self.gain=self.calcGain()

        
    def calcGain(self):
        r,c=len(self.rows),len(self.colsPos)+len(self.colsNeg)
        if c==0:
            return 0
        #return r*c*self.bp-self.bp*(r+c)-r*math.ceil(math.log2(c))
        return r*c*self.bp-self.bp*(r+c)
    
    def _getCols(self,pos=True):
        cSets=[]
        if pos:
            for r_ind in self.rows:
                r=w[r_ind]
                cList=np.argwhere(r==1).squeeze().tolist()
                if type(cList)==int:
                    cList=tuple((cList,))
                #print(cList)
                cSets.append(set(cList))
            result=cSets[0]
            for i in range(1,len(cSets)):
                result=result & cSets[i]
        else:
            for r_ind in self.rows:
                r=w[r_ind]
                cList=np.argwhere(r==-1).squeeze().tolist()
                #print(cList)
                cSets.append(set(cList))
            result=cSets[0]
            for i in range(1,len(cSets)):
                result=result & cSets[i]

        return result
    
    def __str__(self):
        result="r_set:{}\nc_setPos:{}\nc_setNeg:{}\ngain:{}".format(self.r_set,self.c_setPos,self.c_setNeg,self.gain)
        return result
    
    def __repr__(self):
        result="r_set:{}\nc_setPos:{}\nc_setNeg:{}\ngain:{}".format(self.r_set,self.c_setPos,self.c_setNeg,self.gain)
        return result
    @classmethod
    def merge(cls,cover1,cover2):
        rst=[]
        r_set=cover1.r_set | cover2.r_set
        c_set0Pos=cover1.c_setPos & cover2.c_setPos
        c_set0Neg=cover1.c_setNeg & cover2.c_setNeg
        c_set1Pos=cover1.c_setPos & cover2.c_setNeg
        c_set1Neg=cover1.c_setNeg & cover2.c_setPos
        rstCover0=Covering((r_set),(c_set0Pos),(c_set0Neg),cover1.bp)
        rstCover1=Covering((r_set),(c_set1Pos),(c_set1Neg),cover1.bp)
        if rstCover0.gain>0:
            rst.append(rstCover0)
        if rstCover1.gain>0:
            rst.append(rstCover1)
        return(rst)

class Pairing():
    def __init__(self,rows,sharings,unUsedCols,unCombinedSharings):
        self.sharings=sharings
        self.rows=rows
        self.unUsedCols=unUsedCols
        self.unCombinedSharings=unCombinedSharings
        self.gain=self.calcGain()

    def calcGain(self):
        rst=0
        for sh in self.sharings:
            rst+=sh.gain
        for sh in self.unCombinedSharings:
            rst+=sh.gain
        return rst


    @classmethod
    def merge(cls,pairing1,pairing2):
        newUnUsedCols=pairing1.unUsedCols|pairing2.unUsedCols
        newRows=pairing1.rows|pairing2.rows
        rstNewSharings=[]
        for sh1 in pairing1.sharings:
            uncombined_sharing_weight=sh1.c_setPos|sh1.c_setNeg
            for sh2 in pairing2.sharings:
                newSharings=Covering.merge(sh1,sh2)
                for sh in newSharings:
                    # print(uncombined_sharing_weight)
                    # print(sh.unUsedCols)
                    uncombined_sharing_weight=uncombined_sharing_weight-sh.c_setPos-sh.c_setNeg
                    rstNewSharings.append(sh)
            newUnUsedCols=newUnUsedCols|uncombined_sharing_weight
        return Pairing(newRows,rstNewSharings,newUnUsedCols,[])







def computeGain(nRows,nCols,bp=10): #given in length
    r,c=nRows,nCols
    oriCost=r*c*bp
    #newCost=bp*(r+c)+r*math.ceil(math.log2(c))
    newCost=bp*(r+c)
    return oriCost-newCost

def findInitPairing(w,bp):
    r,c=w.shape[0],w.shape[1]
    #bp=remainbit*2
        
    G = nx.complete_graph(r)
    for i in range(r):
        for j in range(i+1,r):
            #print(i,',',j)
            colsSame=np.argwhere((w[i]==w[j])&(w[i]!=0)).squeeze()
            colsDiff=np.argwhere((w[i]==-w[j])&(w[i]!=0)).squeeze()
            #nCols=max(len(colsDiff),len(colsSame))
            # print("i,j=",i,j)
            # print(colsSame)
            # print(colsDiff)
            # print(colsSame.shape)
            # print(colsDiff.shape)
            if len(colsSame.shape)==0:
                nCols=1  
            else:
                nCols=colsSame.shape[0]
            if len(colsDiff.shape)==0:
                nCols+=1
            else:
                nCols+=colsDiff.shape[0]
            G[i][j]['weight']=computeGain(2,nCols,bp)
    
            
    maxMatch=nx.algorithms.matching.max_weight_matching(G)
    pairs=[(pair,G[pair[0]][pair[1]]['weight']) for pair in maxMatch]#[((row0,row1),weight),...]
    pairs.sort(key=lambda p:p[1])#ascending sort by weight
    #pairs.sort(key=lambda p:p[1],reverse=True)#descending sort by weight
    #initPairings=[Covering(list(pair[0]),bp=bp) for pair in pairs]
    fullSet=set([i for i in range(w.shape[1])])
    initPairings=[]
    for pair in pairs:
        i=pair[0][0]
        j=pair[0][1]
        colsSamePos=np.argwhere((w[i]==w[j])&(w[i]==1)).squeeze().tolist()
        colsSameNeg=np.argwhere((w[i]==w[j])&(w[i]==-1)).squeeze().tolist()
        colsDiffPos=np.argwhere((w[i]==-w[j])&(w[i]==1)).squeeze().tolist()
        colsDiffNeg=np.argwhere((w[i]==-w[j])&(w[i]==-1)).squeeze().tolist()
        if type(colsSamePos)==int:
            colsSamePos=tuple((colsSamePos,))
        if type(colsSameNeg)==int:
            colsSameNeg=tuple((colsSameNeg,))
        if type(colsDiffPos)==int:
            colsDiffPos=tuple((colsDiffPos,))
        if type(colsDiffNeg)==int:
            colsDiffNeg=tuple((colsDiffNeg,))
        unUsedCols=fullSet-set(colsSamePos)-set(colsSameNeg)-set(colsDiffPos)-set(colsDiffNeg)
        c1=Covering(set([i,j]),colsSamePos,colsSameNeg,bp)
        c2=Covering(set([i,j]),colsDiffPos,colsDiffNeg,bp)
        sharings=[]
        if c1.gain>0:
            sharings.append(c1)
        if c2.gain>0:
            sharings.append(c2)
        #usedCols=sharings[0].c_setPos|sharings[0].c_setNeg|sharings[1].c_setPos|sharings[1].c_setNeg
        initPairings.append(Pairing(set([i,j]),sharings,unUsedCols,[]))
    print("len(initPairings):",len(initPairings))
    return initPairings


def findPairingSet(unSharedWeight,bp):
    r=len(unSharedWeight)
    #print("len(unSharedWeight):",len(unSharedWeight))
    #bp=remainbit*2
        
    G = nx.complete_graph(r)
    for i in range(r):
        for j in range(i+1,r):
            #print(i,',',j)
            #picked two rows i and j
            colsSame=(unSharedWeight[i][0]&unSharedWeight[j][0])|(unSharedWeight[i][1]&unSharedWeight[j][1])
            colsDiff=(unSharedWeight[i][0]&unSharedWeight[j][1])|(unSharedWeight[i][1]&unSharedWeight[j][0])
            #nCols=max(len(colsDiff),len(colsSame))
            # print("i,j=",i,j)
            # print(colsSame)
            # print(colsDiff)
            # print(colsSame.shape)
            # print(colsDiff.shape)
            nCols=len(colsSame)+len(colsDiff)
            G[i][j]['weight']=computeGain(2,nCols,bp)
    
            
    maxMatch=nx.algorithms.matching.max_weight_matching(G)
    #print("len(maxMatch):",len(maxMatch))
    pairs=[(pair,G[pair[0]][pair[1]]['weight']) for pair in maxMatch]#[((row0,row1),weight),...]
    pairs.sort(key=lambda p:p[1])#ascending sort by weight
    #pairs.sort(key=lambda p:p[1],reverse=True)#descending sort by weight
    #initPairings=[Covering(list(pair[0]),bp=bp) for pair in pairs]
    fullSet=set([i for i in range(w.shape[1])])
    rstPairings=[]
    for pair in pairs:
        i=pair[0][0]
        j=pair[0][1]
        colsSamePos=unSharedWeight[i][0]&unSharedWeight[j][0]
        colsSameNeg=unSharedWeight[i][1]&unSharedWeight[j][1]
        colsDiffPos=unSharedWeight[i][0]&unSharedWeight[j][1]
        colsDiffNeg=unSharedWeight[i][1]&unSharedWeight[j][0]
        
        unUsedCols=fullSet-colsSamePos-colsSameNeg-colsDiffPos-colsDiffNeg
        coverSame=Covering(set([i,j]),colsSamePos,colsSameNeg,bp)
        coverDiff=Covering(set([i,j]),colsDiffPos,colsDiffNeg,bp)
        sharings=[]
        if coverSame.gain>0:
            sharings.append(coverSame)
        if coverDiff.gain>0:
            sharings.append(coverDiff)
        if sharings!=[]:
        	rstPairings.append(Pairing(set([i,j]),sharings,unUsedCols,[]))
    #print("len(rstPairings):",len(rstPairings))
    return rstPairings


def countUsedCols(pairings):
    rst=0
    for pair in pairings:
        for sh in pair.sharings:
            rst+=len(sh.c_setNeg|sh.c_setPos)
    return rst

#device=torch.device("cuda" if torch.cuda.is_available() else "cpu")

#main
modelFolder="./"
numBits=5
convs=["conv11","conv21","conv22"]
fcs=["dense1","dense"]
# log=open(modelFolder+"covering_log_Booth.txt",'w')
# log.write("| layer | cost(opt/no_opt) | #LUT | nets |\n| ----- | ---- | ---- | ---- |\n")
layers=[]
for i in range(len(convs)):
    layers.append(convs[i])
for i in range(len(fcs)):
    layers.append(fcs[i])

#layers=['conv21']

convCostCount=0
fcCostCount=0
for lind,l in enumerate(layers):
    print('\n')
    print(l)
    with open(f"parseRet/{l}.npy",'rb') as f:
        w=np.load(f)
        w=w.astype(int)
    #t=torch.from_numpy(m)
    #w=t.numpy()
    bp=numBits*2
    initPairings=findInitPairing(w,bp)
    #print("init pairs:")
    #for p in initPairings:
    #    print(p)
    
    #resultPairings=initPairings
    resultPairings=[]
    while len(initPairings)>0:
        cover1=initPairings[0]
        maxBenefit=0
        maxInd=-1
        for i in range(1,len(initPairings)):
            gain=Pairing.merge(cover1,initPairings[i]).gain
            benefit=gain-cover1.gain-initPairings[i].gain
            #print("benefit:",benefit)
            if benefit>maxBenefit:
                maxBenefit=benefit
                maxInd=i
        if maxInd!=-1:
            initPairings[i]=Pairing.merge(cover1,initPairings[maxInd])
        else:
            resultPairings.append(cover1)
        del initPairings[0]
    
    totalGain=0
    for i,p in enumerate(resultPairings):
        #print("pairing {}:\n".format(i),p,'\n')
        totalGain+=p.gain
    # print("total gain:",totalGain)
    # print("cost before opt:",np.abs(w).sum()*bp)
    # print("reduction:",totalGain/(np.abs(w).sum()*bp))

    resultCoverings=[]
    for pair in resultPairings:
        for cover in pair.sharings:
            resultCoverings.append(cover)
    print("\nround1, newSharedWeightCount:",countUsedCols(resultPairings))
    

    ###############################
    #gather information for post pairing
    unSharedWeight=dict()#the unshared weights for w, given in {row:[unshared 1,unshared -1]}
    for r in range(w.shape[0]):
        posCols=np.argwhere(w[r]==1).squeeze().tolist()
        if type(posCols)==int:
            posCols=set((posCols,))
        else:
            posCols=set(posCols)
        negCols=np.argwhere(w[r]==-1).squeeze().tolist()
        if type(negCols)==int:
            negCols=set((negCols,))
        else:
            negCols=set(negCols)
        unSharedWeight[r]=[posCols,negCols]
        assert(len(posCols)+len(negCols)==abs(w[r]).sum())
    for cover in resultCoverings:
        for r in cover.r_set:
            # if r==287:
            #     print(cover)
            #nonZeroCols=set(np.argwhere(w[r]!=0).squeeze().tolist())
            if len(cover.c_setPos)>=1:
                if w[r][list(cover.c_setPos)[0]]==1:
                    unSharedWeight[r][0]=unSharedWeight[r][0]-cover.c_setPos
                    unSharedWeight[r][1]=unSharedWeight[r][1]-cover.c_setNeg
                else:
                    unSharedWeight[r][0]=unSharedWeight[r][0]-cover.c_setNeg
                    unSharedWeight[r][1]=unSharedWeight[r][1]-cover.c_setPos
            elif len(cover.c_setNeg)>=1:
                if w[r][list(cover.c_setNeg)[0]]==-1:
                    unSharedWeight[r][0]=unSharedWeight[r][0]-cover.c_setPos
                    unSharedWeight[r][1]=unSharedWeight[r][1]-cover.c_setNeg
                else:
                    unSharedWeight[r][0]=unSharedWeight[r][0]-cover.c_setNeg
                    unSharedWeight[r][1]=unSharedWeight[r][1]-cover.c_setPos
            
    #run several rounds for post pairing
    for run in range(500):
        print("run:",run)

        postPairing=findPairingSet(unSharedWeight,bp)
        #print("postPairing:",postPairing)
        #print("newSharedWeightCount:",countUsedCols(postPairing))
        if countUsedCols(postPairing)==0:
            #print("no further improve when round=",run)
            break
        
        for i,p in enumerate(postPairing):
            #print("pairing {}:\n".format(i),p,'\n')
            totalGain+=p.gain
            if p.sharings!=[] and p.gain>0:
                resultCoverings+=(p.sharings)
        # print("total gain:",totalGain)
        # print("cost before opt:",np.abs(w).sum()*bp)
        # print("reduction:",totalGain/(np.abs(w).sum()*bp))


        #unSharedWeight=dict()
        # for r in range(w.shape[0]):
        #     posCols=set(np.argwhere(w[r]==1).squeeze().tolist())
        #     negCols=set(np.argwhere(w[r]==-1).squeeze().tolist())
        #     unSharedWeight[r]=[posCols,negCols]
        for pair in postPairing:
            for cover in pair.sharings:
                for r in cover.r_set:
                    if r==287:
                        print(cover)
                    #nonZeroCols=set(np.argwhere(w[r]!=0).squeeze().tolist())
                    if len(cover.c_setPos)>=1:
                        if w[r][list(cover.c_setPos)[0]]==1:
                            unSharedWeight[r][0]=unSharedWeight[r][0]-cover.c_setPos
                            unSharedWeight[r][1]=unSharedWeight[r][1]-cover.c_setNeg
                        else:
                            unSharedWeight[r][0]=unSharedWeight[r][0]-cover.c_setNeg
                            unSharedWeight[r][1]=unSharedWeight[r][1]-cover.c_setPos
                    elif len(cover.c_setNeg)>=1:
                        if w[r][list(cover.c_setNeg)[0]]==-1:
                            unSharedWeight[r][0]=unSharedWeight[r][0]-cover.c_setPos
                            unSharedWeight[r][1]=unSharedWeight[r][1]-cover.c_setNeg
                        else:
                            unSharedWeight[r][0]=unSharedWeight[r][0]-cover.c_setNeg
                            unSharedWeight[r][1]=unSharedWeight[r][1]-cover.c_setPos
        #print(unSharedWeight)            

    print("total gain:",totalGain)
    print("cost after opt:",np.abs(w).sum()*bp-totalGain)
    print("cost before opt:",np.abs(w).sum()*bp)
    print("reduction:",totalGain/(np.abs(w).sum()*bp))
    # log.write(f"|{l}|{np.abs(w).sum()*bp-totalGain}/{np.abs(w).sum()*bp}| | |\n")
    # if lind<5:
    #     convCostCount+=np.abs(w).sum()*bp-totalGain
    # else:
    #     fcCostCount+=np.abs(w).sum()*bp-totalGain
    ################################################################    
    #save results

    # for c in resultCoverings:
    #     if (len(c.c_setNeg)+len(c.c_setPos))<=0:
    #         print(c)
    #         print(c.gain,c.gain<=0.1)
    for ind,c in enumerate(resultCoverings):
        if c.gain<=0.1:
            print(c)
            for row in list(c.r_set):
                for col in list(c.c_setPos|c.c_setNeg):
                    unSharedWeight[row][0].add(col)
            resultCoverings.remove(c)
    # for ind,c in enumerate(resultCoverings):
    #     if len(c.c_setPos)==0 and len(c.c_setNeg)==0:
    #         print("ind:",ind,c)
    #         resultCoverings.remove(c)

    pickle.dump(resultCoverings,open(f"{modelFolder}covering/{l}SharedW_3.pkl",'wb'))

    rstUnSharedW=dict()
    for r in range(w.shape[0]):
        rstUnSharedW[r]=unSharedWeight[r][0]|unSharedWeight[r][1]
    pickle.dump(rstUnSharedW,open(f"{modelFolder}covering/{l}UnsharedW_3.pkl",'wb'))
    #break


# log.close()


# print('conv cost:',convCostCount)
# print('fc cost:',fcCostCount)
# print('total cost:',convCostCount+fcCostCount)