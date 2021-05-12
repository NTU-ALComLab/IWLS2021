#TODO: add fringe feature extraction

import numpy as np
from sklearn.tree import DecisionTreeClassifier

class DTree():
    def __init__(self, idx=None, verbose=True, dtParams=dict()):
        self.idx = idx
        self.verbose = verbose
        self.dtree = DecisionTreeClassifier(**dtParams)

    # train the dtree with the given data and labels
    def train(self, data, labels):
        self.dtree.fit(data, labels)
        if self.verbose:
            _, acc = self.test(data, labels)
            print('training dt[{}], acc={}'.format(str(self.idx), str(acc)))

    # return the predicted labels of the input data by the dtree
    def predict(self, data):
        return self.dtree.predict(data)

    # return the predictions and accuracy of the dtree on the input data
    def test(self, data, labels):
        preds = self.predict(data)
        acc = np.sum(np.array(preds)==np.array(labels)) / len(labels)
        return preds, acc
