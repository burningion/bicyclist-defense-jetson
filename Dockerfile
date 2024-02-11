FROM dustynv/nanoowl:r36.2.0
# from the nanoowl repo 

# upgrade pillow to fix "UnidentifiedImageError"
RUN pip install pillow --upgrade 
# install rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
RUN git clone git@github.com:rerun-io/rerun.git && cd rerun && ./scripts/setup_dev.sh && pip install --upgrade pip
RUN cd rerun && pip install -r rerun_py/requirements-build.txt && pip3 install "./rerun_py"

