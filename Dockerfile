FROM dustynv/nanoowl:r36.2.0
# from the nanoowl repo 

# upgrade pillow to fix "UnidentifiedImageError"
RUN pip install pillow --upgrade 
RUN apt-get update && apt-get install -y sudo apt-utils
# install rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs |  RUSTUP_PERMIT_COPY_RENAME=1 sh -s -- -y
RUN pip install --pre -f https://build.rerun.io/commit/71ecddb/wheels --upgrade rerun-sdk
RUN cd /opt/nanoowl/ && git pull
RUN cd /opt && git clone https://github.com/NVIDIA-AI-IOT/nanosam && cd nanosam && python3 setup.py develop --user
RUN wget https://nodejs.org/dist/v20.12.0/node-v20.12.0-linux-arm64.tar.xz && tar -xJvf node-v20.12.0-linux-arm64.tar.xz && mv node-v20.12.0-linux-arm64 /usr/local/lib/node
RUN sh -c 'echo "export NODEJS_HOME=/usr/local/lib/node" >> /root/.bashrc' && sh -c 'echo "export PATH=/usr/local/lib/node/bin:$PATH" >> /root/.bashrc'
COPY bicycle-app/requirements.txt /requirements.txt 
RUN pip install -r /requirements.txt