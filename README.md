# IWLS 2021 Programming Contest Submission from Team NTU-ALCOM

## Team Members
- Po-Chun Chien, r07942091@ntu.edu.tw
- Yu-Shan Huang, r09943100@ntu.edu.tw
- Hao-Ren Wang, r09943108@ntu.edu.tw
- Nai-Ning Ji, lesley880813@gmail.com
- Prof. Jie-Hong Roland Jiang (supervisor), jhjiang@ntu.edu.tw

## Our Methods
### Learning Small Circuits
From the 10 classes of CIFAR-10 dataset, we select 2 classes and train a decision tree binary classifier from the selected subset of dataset. In total, there are *C(10, 2) = 45* binary classifers for each class-pair, and their outputs are used for voting the final prediction. This approach is often referred to as the one-against-one (OAO) method when constructing a multi-class classifier with binary classifiers.

### Learning Medium Circuits
We train 10 'small' classifers described in the previous section with different subsets of the dataset. The final prediction is decided by majority voting of the 10 classifers.



### Others
We also apply the following methods on the CIFAR-10 dataset.
- Image downsampling.
- Image augmentation.
- Truncating several least significant bits of each image pixel.

## Our Submission
The 3 AIGs `small.aig`, `medium.aig` and `large.aig` can be found in `submit_AIGs`. Their sizes and accuracy on the testing dataset are listed below.

|                   | `small.aig` | `medium.aig`| `large.aig` |
|-------------------|-------------|-------------|-------------|
| size (#AIG-nodes) |       9,697 |      97,350 |     995,247 |
|  testing acc. (%) |       39.31 |       44.69 |       54.68 |

We only use the CIFAR-10 testing data **ONCE** for each submitted circuit in the 3 size categories for the purpose of final evaluation right before the submission. That is, we never use the testing dataset during the the course of our research.

## Requirements
Please install the required pip packages specified in `requirements.txt`.
```
pip3 install -r requirements.txt
```
We also provide the `Dockerfile` to build the docker image capable of executing our codes.

## How To Run
1. Clone and build ABC in `tools/abc/`.
```
cd tools
git clone git@github.com:berkeley-abc/abc.git
cd abc
make
cd ../..
```

2. Clone and build YOSYS in `tools/yosys/`.
```
cd tools
git clone git@github.com:YosysHQ/yosys.git
cd yosys
make
cd ../..
```

3. To generate the small circuit (with no more than 10,000 AIG-nodes), run the script `small.py`. The output circuit can be found at `small/small.aig`.
```
python3 small.py
```

4. To generate the medium circuit (with no more than 100,000 AIG-nodes), run the script `medium.py`. The output circuit can be found at `medium/medium.aig`.
```
python3 medium.py
```

5. To generate the large circuit (with no more than 1,00,000 AIG-nodes), please follow the instructions in `large/`. Unfortunately, we have not had enough time to integrate all the procedures into a single script.

\* Note that there is some randomness in our procedures, therefore the results may differ each time. Please let us know if there is any problem executing the programs.