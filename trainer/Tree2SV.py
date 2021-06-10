import numpy as np
from sklearn.tree import _tree

svTxt = \
'''
module DTreeTest(
    input [7:0] data [0:3071],
    output N_OUTPUTS pred
);

assign pred = DECISIONS;

endmodule
'''

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
        getClsStr = lambda i, nCls: '{}\'b{}'.format(str(nCls), ''.join(['1' if (j == i) else '0' for j in range(nCls)]))
        getThre = lambda thr: '{}\'d{}'.format(str(self.nBit), str(int(thr) >> (8 - self.nBit)))
        getFeat = lambda feat: 'data[{}][7:{}]'.format(str(feat), str(8 - self.nBit))
        
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
        no = '' if (self.nOut == 1) else '[{}:0]'.format(str(self.nOut - 1))
        c = self.extract_recur()

        s = svTxt.replace('N_OUTPUTS', no).replace('DECISIONS', c)
        with open(fn, 'w') as fp:
            fp.write(s)
