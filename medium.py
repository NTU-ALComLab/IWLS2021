import utils, trainer, syn, os, math
import numpy as np
from trainer.svUtils import svTemplateTxt, svVarGen, svBitPad, svBitSlice, svWrite
from trainer.BinClfEns import bvPrep, bvPost

def voterGen(clfList, nClass, nOut):
    nSumBit = math.ceil(math.log2(len(clfList) + 1))
    predList, sumList, vvars, body = bvPrep(nClass, clfList, nSumBit, nOut)

    # accumulate votes
    accList = [[] for _ in range(nClass)]
    for i in range(nClass):
        for j in predList:
            if nOut == 1:
                p = ('' if (i == 1) else '~') + j
            else:
                p = svBitSlice(j, i)
            accList[i].append(svBitPad(p, nSumBit-1))

    body += bvPost(sumList, accList, nOut == 1)
    
    return vvars, body
    

def ClfEns(path, name, clfList, nClass, nOut):
    ios = ['data_{}'.format(str(i)) for i in range(32*32*3)] + ['pred']
    vvars = svVarGen([('input', 8, 'data_{}'.format(i), 1) for i in range(32*32*3)])
    vvars += svVarGen([('output', nClass, 'pred', 1)])

    nvars, body = voterGen(clfList, nClass, nOut)

    with open(os.path.join(path, name), 'w') as fp:
        s = svWrite(name, ', '.join(ios), vvars + nvars, body)
        fp.write(s)


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
    'ccp_alpha': 0.0004,
}

x = utils.loadConfig('data/raw/train_data.pk')
data, labels = x['data'], x['labels']

m = 10
n = len(data) // m
data_list = [data[i*n : (i+1)*n] for i in range(m)]
lab_list = [labels[i*n : (i+1)*n] for i in range(m)]

output_path = 'medium'
os.makedirs(output_path, exist_ok=True)

trs, clfList = [], []
for i in range(m):
    data_ = np.concatenate([data_list[j] for j in range(m) if (i != j)])
    lab_ = np.concatenate([lab_list[j] for j in range(m) if (i != j)]).tolist()
    #print(data_.shape, lab_.shape)

    data_, lab_ = utils.dataAug(data_, lab_, 1, 10)
    data_, lab_ = utils.imgPrepro(data_, lab_, **preConfig)
    #data2_, lab2_ = utils.imgPrepro(data_list[i], lab_list[i], **preConfig)

    tr = trainer.getTrainer(clfType='dt', mode='oao', verbose=False, clfParams=dtParams)
    acc = tr.train(data_, lab_, nJob=10)
    #acc = tr.train(data_, lab_, data_list[i], lab_list[i], nJob=45)
    #print(i, acc)

    mName = 'm{}_'.format(str(i))
    tr.dump(output_path, 8-preConfig['nLSB'], mName)

    clfList.append(mName + 'predictor')
    trs.append(tr)

ClfEns(output_path, 'medium.v', clfList, 10, 10)
log = syn.syn(os.path.join(output_path, '*.v'), os.path.join(output_path, 'medium.aig'))
log = utils.loadConfig(log)

data, labels = utils.imgPrepro(data, labels, **preConfig)
preds = np.array([tr.predict(data, 10) for tr in trs], dtype=np.uint8)

# preds.shape = (nClf, nData)
res = np.zeros((10, preds.shape[1]))
for i in range(preds.shape[0]):
    for j in range(preds.shape[1]):
        res[preds[i, j], j] += 1
res_ = np.argmax(res, axis=0)
acc = np.sum(np.array(res_)==np.array(labels)) / len(labels)

print('training acc:', acc[0])
print('circuit size:', log['and'])