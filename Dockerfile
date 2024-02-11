FROM dustynv/nanoowl:r36.2.0
# from the nanoowl repo 

# upgrade pillow to fix "UnidentifiedImageError"
RUN pip install pillow --upgrade 
RUN apt-get update && apt-get install -y sudo apt-utils
# install rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs |  RUSTUP_PERMIT_COPY_RENAME=1 sh -s -- -y
RUN git clone https://github.com/rerun-io/rerun && cd rerun && ./scripts/setup_dev.sh && pip install --upgrade pip
RUN cd rerun && pip install -r rerun_py/requirements-build.txt && pip3 install "./rerun_py"

