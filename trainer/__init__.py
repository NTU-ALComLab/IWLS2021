from .ClfTrainer import Trainer
from .DTree import DTree
from .RForest import RForest
from .DForest import DForest

dtParams = {
    'criterion': 'entropy',
    #'max_depth': 30,
    'class_weight': 'balanced',
    #'ccp_alpha': 0.015,
}

rfParams = {
    'n_estimators': 50,
    'criterion': 'entropy',
    'max_depth': 20,
    'n_jobs': 2,
    'class_weight': 'balanced_subsample',
    #'ccp_alpha': 0.015,
}

dfParams = {
    'max_layers': 10,
    'criterion': 'entropy',
    'n_estimators': 2,
    'n_trees': 40,
    'max_depth': 15,
    'backend': 'sklearn',
    'n_tolerant_rounds': 3,
    'partial_mode': True,
    #'n_jobs': 1,
    #'random_state': None,
    #'verbose': 1,
}

#lutParams = {}

def getTrainer(clfType='dt', nClass=10, mode='dir', verbose=True, clfParams=None):
    if clfType == 'dt':
        params = dtParams if (clfParams is None) else clfParams
        clf = DTree
    elif clfType == 'rf':
        params = rfParams if (clfParams is None) else clfParams
        clf = RForest
    elif clfType == 'df':
        params = dfParams if (clfParams is None) else clfParams
        params['verbose'] = 1 if verbose else 0
        clf = DForest
    elif clfType == 'lut':
        raise NotImplementedError()
    else:
        print('clfType {} not supported.'.format(clfType))
        assert False
    return Trainer(clf, nClass, mode, verbose, params)