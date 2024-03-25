FROM dustynv/nanoowl:r36.2.0
# from the nanoowl repo 

# upgrade pillow to fix "UnidentifiedImageError"
RUN pip install pillow --upgrade 
RUN apt-get update && apt-get install -y sudo apt-utils
# install rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs |  RUSTUP_PERMIT_COPY_RENAME=1 sh -s -- -y
RUN pip install --pre -f https://build.rerun.io/commit/71ecddb/wheels --upgrade rerun-sdk
RUN cd /opt/nanoowl/ && git pull
