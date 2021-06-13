import pickle as pk
import json as js
import yaml as ym

#  load/dump pickle files
def pkDump(x, fn):
    pk.dump(x, open(fn, 'wb'))

def pkLoad(fn):
    return pk.load(open(fn, 'rb'))

# load/dump json files
def jsDump(x, fn):
    js.dump(x, open(fn, 'w'), indent=4)

def jsLoad(fn):
    return js.load(open(fn))

# load/dump yaml files
def ymDump(x, fn):
    with open(fn, 'w') as fp:
        fp.write(ym.safe_dump(x))

def ymLoad(fn):
    return ym.safe_load(open(fn).read())

def loadConfig(fn):
    if fn.endswith('.pk') or fn.endswith('.pickle'):
        return pkLoad(fn)
    elif fn.endswith('.js') or fn.endswith('.json'):
        return jsLoad(fn)
    elif fn.endswith('.ym') or fn.endswith('.yaml'):
        return ymLoad(fn)
    else:
        print('file type of {} not supported.'.format(fn))
        assert False

def dumpConfig(x, fn):
    if fn.endswith('.pk') or fn.endswith('.pickle'):
        return pkDump(x, fn)
    elif fn.endswith('.js') or fn.endswith('.json'):
        return jsDump(x, fn)
    elif fn.endswith('.ym') or fn.endswith('.yaml'):
        return ymDump(x, fn)
    else:
        print('file type of {} not supported.'.format(fn))
        assert False

