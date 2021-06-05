import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.preprocessing import OneHotEncoder
import torchvision
import torchvision.transforms as transforms
from torch.utils.data import Dataset, DataLoader, random_split
import numpy as np
import os
from rich.progress import track
import random
from Models import CNN1, FC1
import argparse
import utils, prepro


def arg_parse():
    parser = argparse.ArgumentParser(
        description='parser for boolean neural netword')

    parser.add_argument('--data_dir',
                        type=str,
                        help="root path to data directory")

    parser.add_argument('--save_dir',
                        type=str,
                        help="directory for saving models")

    args = parser.parse_args()

    return args


class BoolFuncDataset(Dataset):
    def __init__(self, filePath):
        self.filePath = filePath
        raw_data = utils.pkLoad(filePath)
        self.data = prepro.imgPrepro(raw_data["data"],
                                     # fMergeCh=[True, True, True],
                                     nStride=2,
                                     nLSB=6,
                                     fBlast=True)

        self.label = raw_data["labels"]
        # self.label = list(map(lambda x: 0 if x < 5 else 1, raw_data["labels"]))
        # label = np.array(raw_data["labels"]).reshape(-1, 1)
        # encoder = OneHotEncoder()
        # self.label = encoder.fit_transform(label).toarray()

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return self.data[idx], self.label[idx]


def train(train_file, valid_file, save_file):
    batch_size = 32

    trainset = BoolFuncDataset(train_file)
    trainloader = DataLoader(trainset, batch_size=batch_size, shuffle=True)
    validset = BoolFuncDataset(valid_file)
    validloader = DataLoader(validset, batch_size=batch_size, shuffle=False)

    nInput = trainset.data[0].shape[0] * trainset.data[0].shape[1] \
            * trainset.data[0].shape[2] * trainset.data[0].shape[3]
    print(nInput)
    model = FC1(nInput, weight=3)
    model.cuda()
    optimizer = optim.Adam(model.parameters(), lr=1e-5)
    lr_scheduler = (1e-4 - 1e-5) / 50
    criterion = nn.CrossEntropyLoss()
    bestAcc = 0
    bestTrain = 0
    for epoch in range(200):
        train_acc = 0.0
        val_acc = 0.0
        model.train()
        for x, y in track(trainloader):
            optimizer.zero_grad()
            x, y = x.type(torch.float).cuda(), y.type(torch.long).cuda()
            #  output=model(x)
            output = model(x)
            _, train_pred = torch.max(output, 1)
            loss = criterion(output, y)
            loss.backward()
            optimizer.step()
            train_acc += (train_pred.cpu() == y.cpu()).sum().item()
        with torch.no_grad():
            model.eval()
            for data, target in validloader:
                data, target = data.type(torch.float).cuda(), target.type(
                    torch.long).cuda()
                #  valid=model(data)
                valid = model(data)
                _, val_pred = torch.max(valid, 1)
                val_acc += (val_pred.cpu() == target.cpu()).sum().item()
        if epoch < 50:
            optimizer.param_groups[0]['lr'] += lr_scheduler
        elif epoch > 150:
            optimizer.param_groups[0]['lr'] -= lr_scheduler

        train_acc = train_acc / len(trainset)
        val_acc = val_acc / len(validset)
        print("epoch:{}, train acc:{}, valid acc:{}".format(
            epoch, train_acc, val_acc))
        if val_acc > bestAcc:
            bestAcc = val_acc
            torch.save(model.state_dict(), save_file)
    return bestTrain, bestAcc


if __name__ == "__main__":
    args = arg_parse()
    dataName = "{}".format(args.data_dir)
    if not os.path.exists(args.save_dir):
        os.mkdir(args.save_dir)
    train_file = os.path.join(args.data_dir, "train_data.pk")
    valid_file = os.path.join(args.data_dir, "test_data.pk")
    save_file = os.path.join(args.save_dir, "nn_best.pth.tar")
    train(train_file, valid_file, save_file)
