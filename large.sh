cd large/

# train CNN model
mkdir -p temp_weights
mkdir -p weight_array_dense2
python3 train_model.py

# dump circuits (w/o sub-adder sharing) in cktFolder/
mkdir -p cktFolder
python3 revised_gencircuit.py

# detect sharing and dump the newer circuits in modifiedCkt
mkdir -p covering
mkdir -p parseRet
mkdir -p modifiedCkt

cp cktFolder/bind.v modifiedCkt
cp cktFolder/top.v modifiedCkt

python3 parseVerilog.py
python3 oneCoveringBooth_3.py
python3 modifyVerilog.py

# logic synthesis
cd ..
python3 -c "import syn; syn.syn('large/modifiedCkt/*.v', 'large/large.aig')"