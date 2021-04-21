import numpy as np
import pickle as pk

# (un)pickling files
def pkDump(x, fn):
    pk.dump(x, open(fn, 'wb'))

def pkLoad(fn):
    return pk.load(open(fn, 'rb'))


# compute accuracy according to IWLS 2021 rule

# get the label of a 1-hot vector
# each element in the vector should be within the range [0, 1]
def getPredLabel(v):
    assert len(v) == 10  # cifar10 class
    for i in range(10):
        if v[i] > 0.5:
            return i

# compute accuaracy
def getAcc(preds, labels):
    assert len(preds) == len(labels)
    cnt = 0
    for i, j in zip(preds, labels):
        if getPredLabel(i) == j:
            cnt += 1
    return cnt / len(preds)