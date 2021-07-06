mkdir -p temp_weights
mkdir -p weight_array_dense2
python3 train_model.py

mkdir -p cktFolder
python3 revised_gencircuit.py

mkdir -p covering
mkdir -p parseRet
mkdir -p modifiedCkt

cp cktFolder/bind.v modifiedCkt
cp cktFolder/top.v modifiedCkt


python3 parseVerilog.py
python3 oneCoveringBooth_3.py
python3 modifyVerilog.py
