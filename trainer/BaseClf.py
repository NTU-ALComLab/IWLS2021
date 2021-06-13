class BaseClf():
    def __init__(self, idx=None, verbose=True, clfParams=dict()):
        self.idx = idx
        self.verbose = verbose
        self.params = clfParams

    # train the clf with the given data and labels
    def train(self, data, labels):
        raise NotImplementedError()

    # return the predicted labels of the input data by the clf
    def predict(self, data):
        raise NotImplementedError()

    # return the predictions and accuracy of the clf on the input data
    def test(self, data, labels):
        raise NotImplementedError()

    # write the clf into a file
    # fn:   the prefix of the output file
    #       the output file should be: fn + '_' + idx + .format
    #       e.g. dtree_2.sv, lutNet_5.blif ...
    # nBit: number of bits of each pixel in an image
    # nOut: number of primary output
    #       for binary classification, nOut = 1
    #       otherwise for multi-class classification, nOut = nClass
    def dump(self, fn, nBit, nOut):
        raise NotImplementedError()