import numpy as np
from tqdm import tqdm
from sklearn.tree import DecisionTreeClassifier

class DTree():
    def __init__(self, nOuts=10):
        self.verbose = True
    
        # sklearn dtree params
        self.criterion = 'entropy'
        #self.max_depth = max_depth
        #self.ccp_alpha = ccp_alpha
        #self.random_state = randSeed
        
        # dtrees
        self.nOuts = nOuts
        self.dtrees = [DecisionTreeClassifier(criterion=self.criterion) for _ in range(nOuts)]

    def train(self, data, labels):
        # flatten data
        flatDat = data.reshape((data.shape[0], -1))

        # convert labels to one-hot vectors
        oneHotV = np.eye(self.nOuts, dtype=np.int8)[labels]

        for i in tqdm(range(self.nOuts)):
            #print(flatDat.shape, oneHotV[:, i].shape)
            self.dtrees[i].fit(flatDat, oneHotV[:, i])

    def predict(self, data):
        flatDat = data.reshape((data.shape[0], -1))
        preds = [self.dtrees[i].predict(flatDat) for i in range(self.nOuts)]
        return np.transpose(preds)

    def test(self, data, labels):
        pass