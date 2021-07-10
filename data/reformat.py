import pickle as pk
import numpy as np

def read_pickle(fn):
    return pk.load(open(fn, 'rb'), encoding='bytes')

def dump_pickle(x, fn):
    pk.dump(x, open(fn, 'wb'))

def reshape(x):
    assert x.shape == (10000, 3072)
    return x.reshape((10000, 3, 32, 32))

data_path = 'data/raw/'
train_fns = ['data_batch_' + str(i) for i in range(1, 6)]
test_fn = 'test_batch'

train_data, train_labels = np.zeros((0, 3, 32, 32), dtype=np.uint8), []

for train_fn in train_fns:
    train_fn = data_path + train_fn
    x = read_pickle(train_fn)
    train_data = np.concatenate((train_data, reshape(x[b'data'])))
    train_labels += x[b'labels']

x = read_pickle(data_path + test_fn)
test_data, test_labels = reshape(x[b'data']), x[b'labels']

train_all = {'labels': train_labels, 'data': train_data}
test_all = {'labels': test_labels, 'data': test_data}

dump_pickle(train_all, data_path + 'train_data.pk')
dump_pickle(test_all, data_path + 'test_data.pk')
