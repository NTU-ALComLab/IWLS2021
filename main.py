from argparse import ArgumentParser
import os, utils, trainer, syn

def getArgs():
    parser = ArgumentParser(description='sample script for training.')
    parser.add_argument('--data_path', type=str, default='data/raw/train_data.pk')
    parser.add_argument('--output_path', type=str, default=None)
    parser.add_argument('--clf_type', default='dt', type=str, choices=['dt', 'rf', 'df'])  # lut not yet supported
    parser.add_argument('--mode', default='dir', type=str, choices=['dir', 'oaa', 'gag', 'oao'])
    parser.add_argument('--n_jobs', default=1, type=int)
    parser.add_argument('--data_aug', default=4, type=int)
    parser.add_argument('--verbose', action='store_true')
    parser.add_argument('--prepro_config', default=None, type=str)
    parser.add_argument('--train_config', default=None, type=str)
    parser.add_argument('--eval_bin', default='data/raw_bin/data_batch_5.bin', type=str)
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
    train_data, train_labels = utils.imgPrepro(train_data, train_labels, **preConfig)
    val_data = utils.imgPrepro(val_data, **preConfig)
    if args.verbose: print('data preprocessing: done.')

    # perform training and evaluation
    clfParams = None if (args.train_config is None) else utils.loadConfig(args.train_config)
    tr = trainer.getTrainer(args.clf_type, 10, args.mode, args.verbose, clfParams)
    train_acc, val_acc = tr.train(train_data, train_labels, val_data, val_labels, args.n_jobs)
    if args.verbose: print('training classifier: done.')

    # evaluation
    #_, train_acc = tr.test(train_data, train_labels, args.n_jobs)
    #_, val_acc = tr.test(val_data, val_labels, args.n_jobs)
    #print('val. acc.:', valAcc)

    # write circuits and logging
    if args.output_path is not None:
        os.makedirs(args.output_path, exist_ok=True)
        
        # dump circuits
        tr.dump(args.output_path, 8-preConfig['nLSB'])

        # sythesize into AIG
        model_aig = os.path.join(args.output_path, 'model.aig')
        size_log = syn.syn(os.path.join(args.output_path, '*.v'), model_aig)
        size_log = utils.loadConfig(size_log)
        if args.verbose:
            print('aig_size:', size_log['and'])

        # circuit acc. evaluation
        if args.eval_bin is not None:
            eval_log = syn.eval(model_aig, args.eval_bin)
            eval_log = utils.loadConfig(eval_log)
            eval_log['acc'] = eval_log['correct'] / eval_log['total']
            if args.verbose:
                print('aig_acc:', eval_log['acc'])
        
        # dump log
        #with open(os.path.join(args.output_path, 'acc.log'), 'w') as fp:
        #    fp.write('training acc: {}\n'.format(str(train_acc)))
        #    fp.write('validation acc: {}\n'.format(str(val_acc)))
        log = vars(args)
        log['train_acc'] = float(train_acc)
        log['val_acc'] = float(val_acc)
        log['n_aig'] = size_log['and']
        if args.eval_bin is not None:
            log['aig_acc'] = eval_log['acc']
        utils.dumpConfig(log, os.path.join(args.output_path, 'log.yaml'))

        # dump config
        utils.dumpConfig(preConfig, os.path.join(args.output_path, 'pre_config.yaml'))
        utils.dumpConfig(tr.clfs[0].params, os.path.join(args.output_path, 'train_config.yaml'))

