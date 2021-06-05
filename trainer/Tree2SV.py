import numpy as np
from sklearn.tree import _tree

svTxt = \
'''
module DTreeTest(
    input [7:0] data [0:3071],
    output [9:0] pred
);

assign pred = DECISIONS;

endmodule
'''

def extract_recur(dtree, nBit, nodeId=0):
    # small utilities
    getClsStr = lambda i, n: '{}\'b{}'.format(str(n), ''.join(['1' if (j == i) else '0' for j in range(n)]))
    getThr = lambda thr, nBit: '{}\'d{}'.format(str(nBit), str(int(thr)))
    getFeat = lambda feat, nBit: 'data[{}][7:{}]'.format(str(feat), str(8 - nBit))
    
    # termination: leaf node
    if dtree.feature[nodeId] == _tree.TREE_UNDEFINED:
        iCls, nCls = np.argmax(dtree.value[nodeId]), len(dtree.value[nodeId][0])
        return getClsStr(iCls, nCls)
    
    # recursive
    cond = '{} <= {}'.format(getFeat(dtree.feature[nodeId], nBit), getThr(dtree.threshold[nodeId], nBit))
    left = extract_recur(dtree, nBit, dtree.children_left[nodeId])
    right = extract_recur(dtree, nBit, dtree.children_right[nodeId])
    return '({}) ? ({}) : ({})'.format(cond, left, right)

def tree2sv(dt, fn, nBit=8):
    assert dt.n_features_ == 3072
    c = extract_recur(dt.tree_, nBit)
    s = svTxt.replace('DECISIONS', c)
    with open(fn, 'w') as fp:
        fp.write(s)
