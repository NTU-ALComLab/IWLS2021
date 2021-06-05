import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F


class CNN1(nn.Module):
    def __init__(self):
        super(CNN1, self).__init__()
        self.conv1 = nn.Sequential(nn.Conv2d(1, 10, 2, 1, 0), nn.ReLU())
        self.conv2 = nn.Sequential(nn.Conv2d(10, 20, 2, 1, 0), nn.ReLU())
        self.fc1 = nn.Sequential(nn.Linear(20 * 12, 1), nn.Sigmoid())

    def forward(self, x):
        x = x.view(-1, 1, 4, 8)
        x = self.conv2(self.conv1(x))
        x = x.view(-1, 20 * 12)
        x = self.fc1(x)
        return x


def init_weights(m):
    if type(m) == nn.Linear:
        torch.nn.init.xavier_uniform_(m.weight)
        m.bias.data.fill_(0.01)

class FC1(nn.Module):
    def __init__(self, nInput, weight):
        super(FC1, self).__init__()
        self.nInput = nInput
        print("weight = {}".format(weight))

        self.fc1 = nn.Linear(self.nInput, self.nInput)
        self.fc1.apply(init_weights)
        self.fc2 = nn.Linear(self.nInput, self.nInput)
        self.fc2.apply(init_weights)
        self.fc3 = nn.Linear(self.nInput, int(self.nInput * 1.5))
        self.fc3.apply(init_weights)
        self.fc4 = nn.Linear(int(self.nInput * 1.5), self.nInput)
        self.fc4.apply(init_weights)
        self.fc5 = nn.Linear(self.nInput, 12)
        self.fc5.apply(init_weights)
        self.fc6 = nn.Linear(12, 10)
        self.fc6.apply(init_weights)
        self.flatten = nn.Flatten(1)
        self.weight = weight
        self.activate = nn.Sigmoid()
        self.dropout = nn.Dropout(p=0.1)

    def forward(self, x):
        # x = x.view(8, -1)
        x = self.flatten(x)
        x1 = self.activate(self.weight * self.dropout(self.fc1(x)))
        x2 = self.activate(self.weight * self.dropout(self.fc2(x1)))
        x3 = self.activate(self.weight * self.dropout(self.fc3(x2)))
        x4 = self.activate(self.weight * self.dropout(self.fc4(x3)))
        x5 = self.activate(self.weight * self.dropout(self.fc5(x4)))
        x6 = self.fc6(x5)
        return x6
