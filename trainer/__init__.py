from .ClfTrainer import Trainer
from .DTree import DTree
from .RForest import RForest

dtParams = {
    'criterion': 'entropy',
    #'max_depth': 30,
    'class_weight': 'balanced',
    #'ccp_alpha': 0.015,
}

rfParams = {
    'n_estimators': 100,
    'criterion': 'entropy',
    'max_depth': 20,
    'n_jobs': 1,
    'class_weight': 'balanced_subsample',
    #'ccp_alpha': 0.015,
}

#lutParams = {}

def getTrainer(clfType='dt', nClass=10, mode='dir', verbose=True, clfParams=None):
    if clfType == 'dt':
        params = dtParams if (clfParams is None) else clfParams
        clf = DTree
    elif clfType == 'rf':
        params = rfParams if (clfParams is None) else clfParams
        clf = RForest
    elif clfType == 'lut':
        raise NotImplementedError()
    else:
        print('clfType {} not supported.'.format(clfType))
        assert False
    return Trainer(clf, nClass, mode, verbose, params)