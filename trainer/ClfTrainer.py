import numpy as np
from scipy.special import comb
from itertools import combinations as combs
from joblib import Parallel, delayed

class Trainer():
    # different training/testing modes for n-class classification:
    # - 'dir': directly predict the labels (non-binary output)
    # - 'oaa': one-against-all, one-hot encoding with n outputs (balanced class weight in dtree is preferred)
    # - 'gag': group-against-group, vote by [C(n, n/2) / ((n+1) % 2 + 1)] binary classifiers (not yet tested if n is odd)
    # - 'oao': one-against-one, vote by C(n, 2) binary classifers
    def __init__(self, clf, nClass=10, mode='dir', verbose=True, clfParams=dict()):
        self.nClass = nClass
        self.mode = mode
        self.verbose = verbose
        self.__initClf__(clf, clfParams)

    # initialize the classifier
    def __initClf__(self, clf, clfParams):
        if self.mode == 'dir':
            n = 1
        elif self.mode == 'oaa':
            n = self.nClass
        elif self.mode == 'gag':
            #n = comb(self.nClass, self.nClass//2, exact=1)
            n = comb(self.nClass, self.nClass//2, exact=1)
            if self.nClass % 2 == 0:
                n //= 2
        elif self.mode == 'oao':
            n = comb(self.nClass, 2, exact=1)
        else:
            print(self.mode, 'mode not supported.')
            assert False
        self.clfs = [clf(i, self.verbose, clfParams) for i in range(n)]
    
    # train the classifier with the given data and labels
    def train(self, data, labels, nJob=1):
        # convert labels according to training mode
        traLabs = self.__traLabPrep__(labels)

        #for dt, lab in zip(self.dtrees, traLabs):
        #    dt.train(flatDat, lab)
        
        # parallel training
        Parallel(n_jobs=nJob, backend='threading')(delayed(clf.train)(data, lab) for clf, lab in zip(self.clfs, traLabs))
        #def f(dt, dat, lab):
        #    dt.train(dat, lab)
        #    return dt
        #self.dtrees = Parallel(n_jobs=self.nJob)(delayed(f)(dt, flatDat, lab) for dt, lab in zip(self.dtrees, traLabs))

        if self.verbose:
            _, acc = self.test(data, labels)
            print('Clf training acc={}'.format(str(acc)))

    # training labels preprocessing
    def __traLabPrep__(self, labels):
        # 'dir': same labels as given
        if self.mode == 'dir':
            return [labels]
        # 'oaa': one-hot encoding of labels
        elif self.mode == 'oaa':
            return np.eye(self.nClass, dtype=np.uint8)[labels].T
        # 'gag': divide all classes into 2 groups, each annotated with 0 and 1 labels
        elif self.mode == 'gag':
            ret = []
            for i, s in enumerate(combs(range(self.nClass), self.nClass//2)):
                if i >= len(self.clfs): break
                s = set(s)
                ret.append([lab in s for lab in labels])
            return np.array(ret, dtype=np.uint8)
        # 'oao': select 2 classes for comparison, annotate the first class with 0, second with 1, and the rest with -1
        elif self.mode == 'oao':
            ret = []
            for s in combs(range(self.nClass), 2):
                x = []
                for lab in labels:
                    if lab == s[0]: x.append(0)
                    elif lab == s[1]: x.append(1)
                    else: x.append(-1)
                ret.append(x)
            return np.array(ret, dtype=np.uint8)
        else:
            print(self.mode, 'mode not supported.')
            assert False

    # return the predicted labels of the input data by the classifier
    def predict(self, data, nJob=1):
        #flatDat = data.reshape((data.shape[0], -1))
        #preds = [dt.predict(flatDat) for dt in self.dtrees]
        preds = Parallel(n_jobs=nJob)(delayed(clf.predict)(data) for clf in self.clfs)

        return self.__predLabPrep__(np.array(preds))

    # predicted labels postprocessing
    # preds.shape = (nClf, nData)
    def __predLabPrep__(self, preds):
        if self.mode == 'dir':
            return preds[0]
        elif self.mode == 'oaa':
            return np.argmax(preds, axis=0)
        elif self.mode == 'gag':
            ret = np.zeros((self.nClass, preds.shape[1]))
            for i, s in enumerate(combs(range(self.nClass), self.nClass//2)):
                if i >= len(self.clfs): break
                s0, s1 = (set(range(self.nClass)) - set(s)), set(s)
                for j in range(preds.shape[1]):
                    assert preds[i, j] in {0, 1}
                    ss = s1 if (preds[i, j] == 1) else s0
                    # accumulate the vote
                    for k in ss: ret[k, j] += 1
            return np.argmax(ret, axis=0)
        elif self.mode == 'oao':
            ret = np.zeros((self.nClass, preds.shape[1]))
            for i, s in enumerate(combs(range(self.nClass), 2)):
                for j in range(preds.shape[1]):
                    k = s[0] if (preds[i, j] == 0) else s[1]
                    ret[k, j] += 1
            return np.argmax(ret, axis=0)
        else:
            print(self.mode, 'mode not supported.')
            assert False

    # return the predictions and accuracy of the classifier on the input data
    def test(self, data, labels, nJob=1):
        preds = self.predict(data, nJob)
        acc = np.sum(np.array(preds)==np.array(labels)) / len(labels)
        return preds, acc

    def dump(self, fn, nBit):
        nOut = self.nClass if (self.mode == 'dir') else 1
        for clf in self.clfs:
            clf.dump(fn, nBit, nOut)