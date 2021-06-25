import os, utils, trainer, syn
import numpy as np

preConfig = {
    'nPeel': 0,
    'nStride': -2,
    'fMergeCh': None, 
    'nLSB': 4,
    'fBlast': False,
    'fPad': True,
}

dtParams = {
    'criterion': 'gini',
    'max_depth': 15,
    'ccp_alpha': 0.0005, #0.001
}

x = utils.loadConfig('data/raw/train_data.pk')
data, labels = x['data'], x['labels']

data, labels = utils.dataAug(data, labels, 1, 10)
data, labels = utils.imgPrepro(data, labels, **preConfig)
tr = trainer.getTrainer(clfType='dt', mode='oao', verbose=False, clfParams=dtParams)
acc = tr.train(data, labels, nJob=10)

output_path = 'small'
os.makedirs(output_path, exist_ok=True)
tr.dump(output_path, 8-preConfig['nLSB'])
syn.syn(os.path.join(output_path, '*.v'), os.path.join(output_path, 'small.aig'))
