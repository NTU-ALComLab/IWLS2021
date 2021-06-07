import numpy as np
import pickle as pk

# (un)pickling files
def pkDump(x, fn):
    pk.dump(x, open(fn, 'wb'))

def pkLoad(fn):
    return pk.load(open(fn, 'rb'))
