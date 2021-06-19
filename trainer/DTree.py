#TODO: add fringe feature extraction

import numpy as np
from sklearn.tree import DecisionTreeClassifier, _tree
from .BaseClf import BaseClf
from .svUtils import svTemplateTxt, svVarGen, svAssign

class Tree2SV_Writer():
    def __init__(self, dtree, nBit=8, nOut=10):
        # check args
        assert dtree.n_features_ == 3072
        assert isinstance(nBit, int) and (nBit >=0) and (nBit <= 8)
        assert isinstance(nOut, int) and (nBit >=1)
        if nOut == 1: assert dtree.n_classes_ == 2
        else: assert dtree.n_classes_ == nOut
        
        #self.dtree = dtree
        self.dtVal = dtree.tree_.value
        self.dtFeat = dtree.tree_.feature
        self.dtThre = dtree.tree_.threshold
        self.dtLc = dtree.tree_.children_left
        self.dtRc = dtree.tree_.children_right
        self.nBit = nBit
        self.nOut = nOut

    def extract_recur(self, nodeId=0):
        # small utilities
        getClsStr = lambda i, nCls: '{}\'b{}'.format(str(nCls), ''.join(['1' if (j == (nCls-1-i)) else '0' for j in range(nCls)]))
        getThre = lambda thr: '{}\'d{}'.format(str(self.nBit), str(int(thr) >> (8 - self.nBit)))
        getFeat = lambda feat: 'data_{}[7:{}]'.format(str(feat), str(8 - self.nBit))
        
        # termination: leaf node
        if self.dtFeat[nodeId] == _tree.TREE_UNDEFINED:
            iCls, nCls = np.argmax(self.dtVal[nodeId]), len(self.dtVal[nodeId][0])
            if self.nOut == 1:
                return '1\'b0' if (iCls == 0) else '1\'b1'
            else:
                return getClsStr(iCls, nCls)
        
        # recursive
        cond = '{} <= {}'.format(getFeat(self.dtFeat[nodeId]), getThre(self.dtThre[nodeId]))
        left = self.extract_recur(self.dtLc[nodeId])
        right = self.extract_recur(self.dtRc[nodeId])
        return '({}) ? ({}) : ({})'.format(cond, left, right)

    def write(self, fn):
        name = fn.split('/')[-1].replace('.v', '')
        ios = ['data_{}'.format(str(i)) for i in range(32*32*3)] + ['pred']
        #vars = svVarGen([('input', 8, 'data', 32*32*3), ('output', self.nOut, 'pred', 1)])
        vvars = svVarGen([('input', 8, 'data_{}'.format(str(i)), 1) for i in range(32*32*3)])
        vvars += svVarGen([('output', self.nOut, 'pred', 1)])
        body = svAssign('pred', self.extract_recur())

        s = svTemplateTxt.replace('MODULE', name) \
                 .replace('IOPORTS', ', '.join(ios)) \
                 .replace('VARS', vvars) \
                 .replace('BODY', body)
        
        with open(fn, 'w') as fp:
            fp.write(s)

def dataPrepro(data, labels):
    # flatten data
    data = data.reshape((data.shape[0], -1))
    
    # remove data with label==-1
    idxs = np.where(labels==-1)[0]
    data, labels = np.delete(data, idxs, axis=0), np.delete(labels, idxs)
    return data, labels

class DTree(BaseClf):
    def __init__(self, idx=None, verbose=True, dtParams=dict()):
        super().__init__(idx, verbose, dtParams)
        self.idx = idx
        self.verbose = verbose
        self.dtree = DecisionTreeClassifier(**dtParams)

    # train the dtree with the given data and labels
    def train(self, data, labels):
        data, labels = dataPrepro(data, labels)
        self.dtree.fit(data, labels)
        if self.verbose:
            _, acc = self.test(data, labels)
            print('training dt[{}], acc={}'.format(str(self.idx), str(acc)))

    # return the predicted labels of the input data by the dtree
    def predict(self, data):
        return self.dtree.predict(data.reshape((data.shape[0], -1)))

    # return the predictions and accuracy of the dtree on the input data
    def test(self, data, labels):
        preds = self.predict(data)
        acc = np.sum(np.array(preds)==np.array(labels)) / len(labels)
        return preds, acc

    # write the dtree into a sv file
    def dump(self, fn, nBit, nOut):
        Tree2SV_Writer(self.dtree, nBit, nOut).write(fn)
        #tree2sv(self.dtree, fn, nBit, nOut)