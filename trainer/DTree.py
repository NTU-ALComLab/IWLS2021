#TODO: add fringe feature extraction

import numpy as np
from sklearn.tree import DecisionTreeClassifier
from .BaseClf import BaseClf
#from ..tree2sv import tree2sv

initParams = {
    'criterion': 'entropy',
    #'max_depth': 30,
    'class_weight': 'balanced',
    #'ccp_alpha': 0.015
}

def dataPrepro(data, labels):
    # flatten data
    data = data.reshape((data.shape[0], -1))
    
    # remove data with label==-1
    idxs = np.where(labels==-1)[0]
    data, labels = np.delete(data, idxs, axis=0), np.delete(labels, idxs)
    return data, labels

class DTree(BaseClf):
    def __init__(self, idx=None, verbose=True, dtParams=initParams):
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
    def dump(self, fn):
        fn += '_{}.sv'.format(str(self.idx))
        raise NotImplementedError()
