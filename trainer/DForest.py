import numpy as np
from deepforest import CascadeForestClassifier
from .BaseClf import BaseClf
from .DTree import dataPrepro
#from .Tree2SV import tree2sv

class DForest(BaseClf):
    def __init__(self, idx=None, verbose=True, dfParams=dict()):
        super().__init__(idx, verbose, dfParams)
        self.idx = idx
        self.verbose = verbose
        self.dforest = CascadeForestClassifier(**dfParams)

    # train the dtree with the given data and labels
    def train(self, data, labels):
        data, labels = dataPrepro(data, labels)
        self.dforest.fit(data, labels)
        if self.verbose:
            _, acc = self.test(data, labels)
            print('training df[{}], acc={}'.format(str(self.idx), str(acc)))

    # return the predicted labels of the input data by the dtree
    def predict(self, data):
        return self.dforest.predict(data.reshape((data.shape[0], -1)))

    # return the predictions and accuracy of the dtree on the input data
    def test(self, data, labels):
        preds = self.predict(data)
        acc = np.sum(np.array(preds)==np.array(labels)) / len(labels)
        return preds, acc

    # write the forest into a sv file
    def dump(self, fn):
        raise NotImplementedError()
