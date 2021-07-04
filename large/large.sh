
python3 revised_circuit.py

mkdir -p covering
mkdir -p parseRet
mkdir -p modifiedCkt

cp bind.v modifiedCkt
cp top.v modifiedCkt


python3 parseVerilog.py
python3 oneCoveringBooth_3.py
python3 modifyVerilog.py
