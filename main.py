from argparse import ArgumentParser
import os, utils, trainer

def getArgs():
    parser = ArgumentParser(description='sample script for training.')
    parser.add_argument('--data_path', type=str, default='./data/raw/train_data.pk')
    parser.add_argument('--clf_type', default='dt', type=str, choices=['dt', 'rf', 'df'])  # lut not yet supported
    parser.add_argument('--mode', default='dir', type=str, choices=['dir', 'oaa', 'gag', 'oao'])
    parser.add_argument('--n_jobs', default=1, type=int)
    parser.add_argument('--data_aug', default=4, type=int)
    parser.add_argument('--verbose', action='store_true')
    parser.add_argument('--prepro_config', default=None, type=str)
    parser.add_argument('--train_config', default=None, type=str)
    args = parser.parse_args()
    print('Running with following command line arguments: {}'.format(args))
    return args

preConfig0 = {
    'nPeel': 0,
    'nStride': 1,
    'fMergeCh': None, 
    'nLSB': 4,
    'fBlast': False,
    'fPad': True,
}

if __name__ == '__main__':
    args = getArgs()
    
    # load training data
    x = utils.loadConfig(args.data_path)
    data, labels = x['data'], x['labels']
    if args.verbose: print('loading data: done.')

    # training(80%) / validation(20%) data split
    n = int(len(data) * 0.8)
    train_data, val_data = data[:n], data[n:]
    train_labels, val_labels = labels[:n], labels[n:]
    if args.verbose: print('splitting data: done.')

    # perform data augmentation
    train_data, train_labels = utils.dataAug(train_data, train_labels, args.data_aug, args.n_jobs)
    if args.verbose: print('data augmentation: done.')

    # perform data preprocessing
    preConfig = preConfig0 if (args.prepro_config is None) else utils.loadConfig(args.prepro_config)
    train_data = utils.imgPrepro(train_data, **preConfig)
    val_data = utils.imgPrepro(val_data, **preConfig)
    if args.verbose: print('data preprocessing: done.')

    # perform training
    clfParams = None if (args.train_config is None) else utils.loadConfig(args.train_config)
    tr = trainer.getTrainer(args.clf_type, 10, args.mode, args.verbose, clfParams)
    tr.train(train_data, train_labels, args.n_jobs)
    if args.verbose: print('training classifier: done.')

    # evaluation
    _, acc = tr.test(val_data, val_labels, args.n_jobs)
    print('val. acc.:', acc)

    # TODO: write circuits...