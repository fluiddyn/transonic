FROM python:3.10-bullseye
LABEL Pierre Augier <pierre.augier@univ-grenoble-alpes.fr>

COPY docker/hgrc $HOME/.hgrc

RUN apt-get update

RUN apt-get install -y --no-install-recommends emacs vim libopenmpi-dev
RUN apt-get install -y --no-install-recommends mercurial python3-pip git
RUN apt-get install -y --no-install-recommends rsync libgl1 xvfb xauth libgl1-mesa-dev

RUN rm -rf /var/lib/apt/lists/*

RUN mkdir -p $HOME/.config/matplotlib
RUN echo 'backend      : agg' > $HOME/.config/matplotlib/matplotlibrc

RUN /usr/bin/python3 -m pip install hg-git hg-evolve
RUN git config --global pull.rebase false

RUN /usr/bin/python3 -m pip install pdm
