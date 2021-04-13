import torch
import torch.nn as nn
import torchvision
import torchvision.transforms as transforms
from torch.utils.data import Dataset, DataLoader, random_split
from tqdm import tqdm

from Model.MobileNet import MobileNetV2

# hyperparameters
device = "cuda" if torch.cuda.is_available() else "cpu"
batch_size = 128
lr = 1e-3
weight_decay = 1e-4
total_epoch = 200

train_tfm = transforms.Compose([
    transforms.RandomResizedCrop((32, 32), (0.2, 1)),
    transforms.RandomHorizontalFlip(0.5),
    transforms.ToTensor(),
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
])

test_tfm = transforms.Compose([
    transforms.ToPILImage(),
    transforms.ToTensor(),
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
])

class Map_Dataset(Dataset):
    def __init__(self, dataset, tfm):
        self.dataset = dataset
        self.tfm = tfm
    def __getitem__(self, index: int):
        return self.tfm(self.dataset[index][0]), self.dataset[index][1]
    def __len__(self):
        return len(self.dataset)

CIFAR10_trainset = torchvision.datasets.CIFAR10(root='./data', train=True,
                                        download=True, transform=train_tfm)
train_set_size = int(len(CIFAR10_trainset) * 0.8)
valid_set_size = len(CIFAR10_trainset) - train_set_size
trainset, validset = random_split(CIFAR10_trainset, [train_set_size, valid_set_size])
# change the transform function for validation set
validset = Map_Dataset(validset, test_tfm)

trainloader = DataLoader(trainset, batch_size=batch_size,
                                          shuffle=True, num_workers=8)
validloader = DataLoader(validset, batch_size=batch_size,
                                          shuffle=True, num_workers=2)

testset = torchvision.datasets.CIFAR10(root='./data', train=False,
                                       download=True, transform=test_tfm)
testloader = DataLoader(testset, batch_size=batch_size,
                                         shuffle=False, num_workers=2)

def train():
    model = MobileNetV2(10)
    model.to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)
    criterion = nn.CrossEntropyLoss()
    best_acc = 0
    for epoch in range(total_epoch):

        # ---------- Training ----------
        # Make sure the model is in train mode before training.
        model.train()

        # These are used to record information in training.
        train_loss = []
        train_accs = []

        # Iterate the training set by batches.
        for batch in tqdm(trainloader):

            # A batch consists of image data and corresponding labels.
            imgs, labels = batch

            # Forward the data. (Make sure data and model are on the same device.)
            logits = model(imgs.to(device))

            # Calculate the cross-entropy loss.
            # We don't need to apply softmax before computing cross-entropy as it is done automatically.
            loss = criterion(logits, labels.to(device))

            # Gradients stored in the parameters in the previous step should be cleared out first.
            optimizer.zero_grad()

            # Compute the gradients for parameters.
            loss.backward()

            # Update the parameters with computed gradients.
            optimizer.step()

            # Compute the accuracy for current batch.
            acc = (logits.argmax(dim=-1) == labels.to(device)).float().mean()

            # Record the loss and accuracy.
            train_loss.append(loss.item())
            train_accs.append(acc)

        # The average loss and accuracy of the training set is the average of the recorded values.
        train_loss = sum(train_loss) / len(train_loss)
        train_acc = sum(train_accs) / len(train_accs)

        # ---------- Validation ----------
        # Make sure the model is in eval mode so that some modules like dropout are disabled and work normally.
        model.eval()

        # These are used to record information in validation.
        valid_loss = []
        valid_accs = []

        # Iterate the validation set by batches.
        for batch in validloader:

            # A batch consists of image data and corresponding labels.
            imgs, labels = batch

            # We don't need gradient in validation.
            # Using torch.no_grad() accelerates the forward process.
            with torch.no_grad():
                logits = model(imgs.to(device))

            # We can still compute the loss (but not the gradient).
            loss = criterion(logits, labels.to(device))

            # Compute the accuracy for current batch.
            acc = (logits.argmax(dim=-1) == labels.to(device)).float().mean()

            # Record the loss and accuracy.
            valid_loss.append(loss.item())
            valid_accs.append(acc)

        # The average loss and accuracy for entire validation set is the average of the recorded values.
        valid_loss = sum(valid_loss) / len(valid_loss)
        valid_acc = sum(valid_accs) / len(valid_accs)
        print(f"[ {epoch + 1:03d}/{total_epoch:03d} ] Train: loss = {train_loss:.3f}, acc = {train_acc:.3}\
                Validation: loss = {valid_loss:.3f}, acc = {valid_acc:.3f}")
        if valid_acc > best_acc:
            best_acc = valid_acc
            torch.save(model.state_dict(), "model.ckpt")
            print('saving model...')


if __name__ == "__main__":
    train()
