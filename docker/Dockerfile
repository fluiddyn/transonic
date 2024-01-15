FROM python:3.10
LABEL Pierre Augier <pierre.augier@univ-grenoble-alpes.fr>

COPY docker/hgrc $HOME/.hgrc

RUN apt-get update

RUN apt-get install -y --no-install-recommends emacs vim libopenmpi-dev
# python3-pip is just for Mercurial (hg-git, hg-evolve)
RUN apt-get install -y --no-install-recommends mercurial python3-pip git
RUN apt-get install -y --no-install-recommends rsync libgl1 xvfb xauth libgl1-mesa-dev

RUN rm -rf /var/lib/apt/lists/*

RUN groupadd -g 1000 appuser && useradd -m -r -u 1000 -g appuser -s /bin/bash appuser -s /bin/bash && usermod -a -G sudo appuser
RUN echo appuser:appuser | chpasswd
USER appuser
ARG HOME=/home/appuser
RUN mkdir -p $HOME/opt
WORKDIR $HOME/opt
RUN echo $USER $HOME $PWD && whoami

ENV PIP_BREAK_SYSTEM_PACKAGES=1

RUN $(hg debuginstall -T '{pythonexe}') -m pip install hg-evolve hg-git --no-cache-dir --user

COPY --chown=appuser:appuser docker/hgrc $HOME/.hgrc

ENV PATH=$HOME/.local/bin:$PATH

RUN mkdir -p $HOME/.config/matplotlib
RUN echo 'backend      : agg' > $HOME/.config/matplotlib/matplotlibrc

RUN git config --global pull.rebase false

RUN python -m pip install pdm nox
