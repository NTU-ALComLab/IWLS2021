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
        r_set=cover1.r_set | cover2.r_set
        c_setPos=cover1.c_setPos & cover2.c_setPos
        c_setNeg=cover1.c_setNeg & cover2.c_setNeg
        return(Covering(list(r_set),list(c_setPos),list(c_setNeg),cover1.bp))


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
        print("pairing1:",pairing1)
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

