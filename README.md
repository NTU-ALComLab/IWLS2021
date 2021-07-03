# IWLS 2021 Programming Contest Submission from Team NTU-ALCOM

## Team Members
- Po-Chun Chien, r07943091@ntu.edu.tw
- Yu-Shan Huang, r09943100@ntu.edu.tw
- Hao-Ren Wang, r09943108@ntu.edu.tw
- Nai-Ning Ji, lesley880813@gmail.com
- Prof. Jie-Hong Roland Jiang (supervisor), jhjiang@ntu.edu.tw

## Our Methods
### Learning Small Circuits
From the 10 classes of CIFAR-10 dataset, we select 2 classes and train a decision tree binary classifier from the selected subset of dataset. In total, there are *C(10, 2) = 45* binary classifers for each class-pair, and their outputs are used for voting the final prediction. This approach is often referred to as the one-against-one (OAO) method when constructing a multi-class classifier with binary classifiers.

### Learning Medium Circuits
We train 10 'small' classifers described in the previous section with different subsets of the dataset. The final prediction is decided by majority voting of the 10 classifers.

### Learning Large Circuits
We train a convolutional neural network model with grouped convolutions and weights restricted to the powers of 2 (i.e. 2^-1, 2^0, 2^1 ...) and 0s. The quantized CNN model is then synthesized with sub-adder sharing to reduce the circuit size.

### Others
We also apply the following methods on the CIFAR-10 dataset.
- Image downsampling.
- Image augmentation.
- Truncating several least significant bits of each image pixel.

To optimize the AIG circuit, we use a combination of [ABC](https://github.com/berkeley-abc/abc) commands _dc2_, _resyn_, _resyn2rs_ and _ifraig_.

## Our Submission
The 3 AIGs `small.aig`, `medium.aig` and `large.aig` (and `large_fixed.aig`[<sup>[1]</sup>](#fn1)) can be found in `submit_AIGs/`. Their sizes and accuracy on the testing dataset are listed below.

|                   | `small.aig` | `medium.aig`| `large.aig` | `large_fixed.aig` |
|-------------------|-------------|-------------|-------------|-------------------|
| size (#AIG-nodes) |       9,697 |      97,350 |     995,247 |           989,043 |
|  testing acc. (%) |       39.31 |       44.69 |       54.68 |             55.82 |

We only use the CIFAR-10 testing data **ONCE** for each submitted circuit in the 3 size categories for the purpose of final evaluation right before the submission. That is, we never use the testing dataset during the the course of our research.

<a class="anchor" id="fn1">[1]</a>: There was originally a bug in our program for large circuit generation which incurred a ≈1% accuracy loss. We managed to fix that bug, however, after the submission deadline (June 25, 2021) of the contest. The newly generated large circuit `large_fixed.aig` is more accurate and at the same time has a smaller size when compared to the previously submimitted one `large.aig`.

## Requirements
Please install the required pip packages specified in `requirements.txt`.
```
pip3 install -r requirements.txt
```
We also provide the `Dockerfile` to build the docker image capable of executing our codes.
```
docker build -t IWLS2021 ./
docker run -it IWLS2021
```

## How To Run [<sup>[2]</sup>](#fn2)
0. It is recommended to clone this repository with the `--recurse-submodules` flag. 
    ```
    git clone --recurse-submodules git@github.com:Po-Chun-Chien/IWLS2021.git
    ```

1. Clone and build [ABC](https://github.com/berkeley-abc/abc) in `tools/abc/`.
    ```
    cd tools
    git clone git@github.com:berkeley-abc/abc.git   # if it hasn't already been cloned
    cd abc
    make
    cd ../..
    ```

2. Clone and build [YOSYS](https://github.com/YosysHQ/yosys) in `tools/yosys/`.
    ```
    cd tools
    git clone git@github.com:YosysHQ/yosys.git      # if it hasn't already been cloned
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

5. To generate the large circuit (with no more than 1,000,000 AIG-nodes), please follow the instructions in `large/`. Unfortunately, we have not had enough time to integrate the overall procedure into a single script. The codes are submitted for your review.

6. If you want to train a decision-tree-based model with customized parameters instead of our fine-tuned ones, run the script `main.py` and use the flag `--help` to see the help messages.
    ```
    python3 main.py     # execute with default arguments
    ```

<a class="anchor" id="fn2">[2]</a>: Note that there is some randomness in our procedures, therefore the results may differ each time. Please let us know if there is any problem executing the programs.
