FROM tensorflow/tensorflow:latest-gpu-py3
RUN apt update -y && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends tzdata
RUN apt install git build-essential clang bison flex \
        libreadline-dev gawk tcl-dev libffi-dev \
        graphviz xdot pkg-config python3 libboost-system-dev \
        libboost-python-dev libboost-filesystem-dev zlib1g-dev -y
COPY . IWLS2021/
RUN git clone https://github.com/berkeley-abc/abc.git IWLS2021/tools/abc || :
RUN cd IWLS2021/tools/abc && make -j8
RUN git clone https://github.com/YosysHQ/yosys.git IWLS2021/tools/yosys || :
RUN cd IWLS2021/tools/yosys && make -j8
RUN pip3 install --upgrade pip
RUN pip3 install -r IWLS2021/requirements.txt
