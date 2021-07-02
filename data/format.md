# Data Format

## Overview
This directory contains the CIFAR-10 dataset downloaded from its [official website](https://www.cs.toronto.edu/~kriz/cifar.html). The Python version of the dataset is located in the folder `raw/`, whereas the binary version is located in `raw_bin/`.

## Size of the Dataset
The CIFAR-10 dataset consists of 60,000 32x32 colour (RGB channels) images with each pixel being 8-bit precision. A single image sums up to 3x32x32x8=24,576 bits of information. All images are classfied into 10 classes and each class contains 6,000 images. There are 50,000 training images (`data_batch` 1~5) and 10000 test images (`test_batch`). 

## How to Load
For the our ease-of-use, we re-organized the orginal Python version of the dataset with the following modifications:  
* Each image, which was originally a 8-bit integer vector of length 3x32x32=3,072, was reshaped into a 3D array of shape (3, 32, 32).
* All the training batches (`data_batch` 1~5) were merged into a single file `train_data.pk`, and the test batch (`test_batch`) is renamed to `test_data.pk`.

Each of the 2 data files is a pickled object containing a dictionary with keys 'labels' and 'data'. Below is a Python3 example of loading the training dataset.
```
import pickle as pk
dataset = pk.load(open('raw/train_data.pk', 'rb'))
labels = dataset['labels']      # a list of 50,000 entries
data = dataset['data']          # a np.uint8 array of shape (50,000, 3, 32, 32)
```

For the binary version of the dataset, we did not make any changes. Please follow the guides provided in the [CIFAR-10 website](https://www.cs.toronto.edu/~kriz/cifar.html) to load the dataset.