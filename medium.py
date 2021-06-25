import utils, trainer
import numpy as np

preConfig = {
    'nPeel': 0,
    'nStride': 2,
    'fMergeCh': None, 
    'nLSB': 4,
    'fBlast': False,
    'fPad': True,
}

dtParams = {
    'criterion': 'gini',
    'max_depth': 15,
    #'class_weight': 'balanced',
    'ccp_alpha': 0.001,
    #'max_leaf_nodes' : 600, 
}

x = utils.loadConfig('data/raw/train_data.pk')
data, labels = x['data'], x['labels']

m = 5
n = len(data) // m
data_list = [data[i*n : (i+1)*n] for i in range(m)]
lab_list = [labels[i*n : (i+1)*n] for i in range(m)]

trs = []
for i in range(m):
    data_ = np.concatenate([data_list[j] for j in range(m) if (i != j)])
    lab_ = np.concatenate([lab_list[j] for j in range(m) if (i != j)]).tolist()
    #print(data_.shape, lab_.shape)

    data_, lab_ = utils.imgPrepro(data_, lab_, **preConfig)
    data2_, lab2_ = utils.imgPrepro(data_list[i], lab_list[i], **preConfig)

    tr = trainer.getTrainer(clfType='dt', mode='oao', verbose=False, clfParams=dtParams)
    acc = tr.train(data_, lab_, data2_, lab2_, 10)
    print(i, acc)

    tr.dump('oao5', 8-preConfig['nLSB'], 'm{}'.format(str(i)))
    trs.append(tr)

