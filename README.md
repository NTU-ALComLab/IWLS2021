# IWLS 2021 Programming Contest Submission from Team NTU-ALCOM

## Team Members
- Po-Chun Chien, r07942091@ntu.edu.tw
- Yu-Shan Huang, r09943100@ntu.edu.tw
- Nai-Ning Ji, lesley880813@gmail.com
- Prof. Jie-Hong Roland Jiang (supervisor), jhjiang@ntu.edu.tw

## Our Methods
1. For small ...


## Our Submission
The 3 AIGs `small.aig`, `medium.aig` and `large.aig` can be found in `submit_AIGs`. Their sizes and accuracy on the testing dataset are listed below.

|                  | `small.aig` | `medium.aig`| `large.aig` |
|------------------|-------------|-------------|-------------|
| size (#AIG-nodes) |           |        |       |
|  testing acc. (%) |           |        |       |

We only use the CIFAR-10 testing data **ONCE** for each submitted circuit in the 3 size categories for the purpose of final evaluation right before the submission. That is, we never use the testing dataset during the the course of our research.

## Requirements

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