import os, math
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from .BaseClf import BaseClf
from .svUtils import svTemplateTxt, svVarGen, svBitPad, svBitSlice, svWrite
from .DTree import dataPrepro, Tree2SV_Writer
from .BinClfEns import bvPrep, bvPost

class RForest2SV_Writer():
    def __init__(self, rforest, nBit=8, nOut=10):
        self.nBit = nBit
        self.nOut = nOut
        #self.rforest = rforest
        self.nClass = rforest.n_classes_
        self.dtrees = rforest.estimators_

        if self.nOut == 1: assert self.nClass == 2
        else: assert self.nOut == self.nClass

    def writeTrees(self):
        for i, j in zip(self.dtList, self.dtrees):
            fn = os.path.join(self.path, i + '.v')
            Tree2SV_Writer(j, self.nBit, self.nOut).write(fn)

    def voterGen(self):
        nSumBit = math.ceil(math.log2(len(self.dtList) + 1))
        predList, sumList, vvars, body = bvPrep(self.nClass, self.dtList, nSumBit, self.nOut)

        # accumulate votes
        accList = [[] for _ in range(self.nClass)]
        for i in range(self.nClass):
            for j in predList:
                if self.nOut == 1:
                    p = ('' if (i == 1) else '~') + j
                else:
                    p = svBitSlice(j, i)
                accList[i].append(svBitPad(p, nSumBit-1))

        body += bvPost(sumList, accList, self.nOut == 1)
        
        return vvars, body
        
    
    def treeEns(self, fn):
        ios = ['data_{}'.format(str(i)) for i in range(32*32*3)] + ['pred']
        vvars = svVarGen([('input', 8, 'data_{}'.format(i), 1) for i in range(32*32*3)])
        vvars += svVarGen([('output', self.nClass, 'pred', 1)])

        nvars, body = self.voterGen()

        with open(fn, 'w') as fp:
            s = svWrite(self.name, ', '.join(ios), vvars + nvars, body)
            fp.write(s)

    def write(self, fn):
        self.path, self.name = fn.rsplit('/', 1)
        self.name = self.name.replace('.v', '')
        self.dtList = ['{}_{}'.format(self.name, str(i)) for i in range(len(self.dtrees))]
        
        self.writeTrees()
        self.treeEns(fn)


class RForest(BaseClf):
    def __init__(self, idx=None, verbose=True, rfParams=dict()):
        super().__init__(idx, verbose, rfParams)
        self.idx = idx
        self.verbose = verbose
        self.rforest = RandomForestClassifier(**rfParams)

    # train the forest with the given data and labels
    def train(self, data, labels):
        data, labels = dataPrepro(data, labels)
        self.rforest.fit(data, labels)
        if self.verbose:
            _, acc = self.test(data, labels)
            print('training rf[{}], acc={}'.format(str(self.idx), str(acc)))

    # return the predicted labels of the input data by the forest
    def predict(self, data):
        return self.rforest.predict(data.reshape((data.shape[0], -1)))

    # return the predictions and accuracy of the forest on the input data
    def test(self, data, labels):
        preds = self.predict(data)
        acc = np.sum(np.array(preds)==np.array(labels)) / len(labels)
        return preds, acc

    # write the forest into a sv file
    def dump(self, fn, nBit, nOut):
        RForest2SV_Writer(self.rforest, nBit, nOut).write(fn)
