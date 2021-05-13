import numpy as np
from dtree import DTree
from scipy.special import comb
from itertools import combinations as combs
from joblib import Parallel, delayed

class DTreeClf():
    # different training/testing modes for n-class classification:
    # - 'dir': directly predict the labels (non-binary output)
    # - '1hot': one-hot encoding with n outputs (balanced class weight in dtree is preferred)
    # - 'vote': vote by C(n, n/2) binary classifiers (C(10, 5) = 252)
    def __init__(self, nClass=10, mode='dir', verbose=True, nJob=10, dtParams=dict()):
        self.nClass = nClass
        self.mode = mode
        self.verbose = verbose
        self.nJob = nJob
        self.dtParams = dtParams
        self.__initClf__()

    # initialize the dtrees
    def __initClf__(self):        
        if self.mode == 'dir':
            n = 1
        elif self.mode == '1hot':
            n = self.nClass
        elif self.mode == 'vote':
            n = comb(self.nClass, self.nClass//2, exact=1)
        else:
            print(self.mode, 'mode not supported.')
            assert False
        self.dtrees = [DTree.DTree(i, self.verbose, self.dtParams) for i in range(n)]
    
    # train the dtree classifier with the given data and labels
    def train(self, data, labels):
        # flatten data
        flatDat = data.reshape((data.shape[0], -1))

        # convert labels according to training mode
        traLabs = self.__traLabPrep__(labels)

        #for dt, lab in zip(self.dtrees, traLabs):
        #    dt.train(flatDat, lab)
        
        # parallel training
        Parallel(n_jobs=10, backend='threading')(delayed(dt.train)(flatDat, lab) for dt, lab in zip(self.dtrees, traLabs))
        #def f(dt, dat, lab):
        #    dt.train(dat, lab)
        #    return dt
        #self.dtrees = Parallel(n_jobs=self.nJob)(delayed(f)(dt, flatDat, lab) for dt, lab in zip(self.dtrees, traLabs))

        if self.verbose:
            _, acc = self.test(data, labels)
            print('DTreeClf training acc={}'.format(str(acc)))

    # training labels preprocessing
    def __traLabPrep__(self, labels):
        if self.mode == 'dir':
            return [labels]
        elif self.mode == '1hot':
            return np.eye(self.nClass, dtype=np.int8)[labels].T
        elif self.mode == 'vote':
            ret = []
            for s in combs(range(self.nClass), self.nClass//2):
                s = set(s)
                ret.append([lab in s for lab in labels])
            return np.array(ret, dtype=np.int8)
        else:
            print(self.mode, 'mode not supported.')
            assert False

    # return the predicted labels of the input data by the dtree classifier
    def predict(self, data):
        flatDat = data.reshape((data.shape[0], -1))
        #preds = [dt.predict(flatDat) for dt in self.dtrees]
        preds = Parallel(n_jobs=self.nJob)(delayed(dt.predict)(flatDat) for dt in self.dtrees)

        return self.__predLabPrep__(np.array(preds))

    # predicted labels postprocessing
    # preds.shape = (nDtree, nData)
    def __predLabPrep__(self, preds):
        if self.mode == 'dir':
            return preds[0]
        elif self.mode == '1hot':
            return np.argmax(preds, axis=0)
        elif self.mode == 'vote':
            ret = np.zeros((self.nClass, preds.shape[1]))
            for i, s in enumerate(combs(range(self.nClass), self.nClass//2)):
                s0, s1 = (set(range(self.nClass)) - set(s)), set(s)
                for j in range(preds.shape[1]):
                    assert preds[i, j] in {0, 1}
                    ss = s1 if (preds[i, j] == 1) else s0
                    # accumulate the vote
                    for k in ss: ret[k, j] += 1
            return np.argmax(ret, axis=0)
        else:
            print(self.mode, 'mode not supported.')
            assert False

    # return the predictions and accuracy of the dtree classifier on the input data
    def test(self, data, labels):
        preds = self.predict(data)
        acc = np.sum(np.array(preds)==np.array(labels)) / len(labels)
        return preds, acc