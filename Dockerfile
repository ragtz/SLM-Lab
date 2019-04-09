# run instructions:
# build image: docker build -t kengz/slm_lab:latest -t kengz/slm_lab:v2.0.0 .
# or use: v=2.0.0 yarn build
# start container: docker run --name lab -dt kengz/slm_lab
# enter container: docker exec -it lab bash
# remove container (forced): docker rm lab -f
# list image: docker images -a
# push image: docker push kengz/slm_lab
# prune: docker system prune

FROM ubuntu:16.04

LABEL maintainer="kengzwl@gmail.com"
LABEL website="https://github.com/kengz/SLM-Lab"

SHELL ["/bin/bash", "-c"]

# create and set the working directory
#RUN mkdir -p /root/SLM-Lab
RUN groupadd -g 999 slm && \
    useradd -r -u 999 -g slm slm && \
    mkdir -p /home/slm/SLM-Lab && \
    chmod -R 777 /home/slm

#WORKDIR /root/SLM-Lab
WORKDIR /home/slm/SLM-Lab

# basic system dependencies for dev, PyTorch, OpenAI gym
RUN apt-get update && \
    apt-get install -y build-essential \
    curl nano git wget zip libstdc++6 \
    libxtst6 libgconf2-4 libnss3 \
    python3-dev zlib1g-dev libjpeg-dev cmake swig python-pyglet python3-opengl libboost-all-dev libsdl2-dev libosmesa6-dev patchelf ffmpeg xvfb && \
    rm -rf /var/lib/apt/lists/*

RUN curl -O https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
    bash Miniconda3-latest-Linux-x86_64.sh -b -p /home/slm/miniconda3 && \
    rm Miniconda3-latest-Linux-x86_64.sh && \
    echo '. /home/slm/miniconda3/etc/profile.d/conda.sh' >> ~/.bashrc && \
    . /home/slm/miniconda3/etc/profile.d/conda.sh && \
    conda --version

# install dependencies, only retrigger on dependency changes
COPY environment.yml environment.yml
# install Python and Conda dependencies
RUN . /home/slm/miniconda3/etc/profile.d/conda.sh && \
    conda create -n lab python=3.6 -y && \
    conda activate lab && \
    conda env update -f environment.yml && \
    conda clean -y --all && \
    rm -rf ~/.cache/pip

# Install extra dependencies for Unity ML agent
# NodeJS and yarn for unity package management and command
RUN curl -sL https://deb.nodesource.com/setup_11.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g yarn
COPY package.json yarn.lock ./
RUN yarn install
RUN . /home/slm/miniconda3/etc/profile.d/conda.sh && \
    conda activate lab && \
    pip install unityagents==0.2.0 && \
    pip uninstall -y tensorflow tensorboard

# copy file at last to not trigger changes above unnecessarily
COPY . .

RUN . /home/slm/miniconda3/etc/profile.d/conda.sh && \
    conda activate lab && \
#    python setup.py test && \
#    pytest --verbose --no-flaky-report test/spec/test_dist_spec.py && \
    yarn reset

CMD ["/bin/bash"]
