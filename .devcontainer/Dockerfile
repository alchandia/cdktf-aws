FROM ubuntu:22.04

ARG USER_ID=1000
ARG TF_VERSION=1.5.7
ARG CDKTF_VERSION=0.18.0
ARG NVM_VERSION=v0.39.5
ENV DEBIAN_FRONTEND=noninteractive

RUN \
  apt update && \
  apt install -y --no-install-recommends \
    python3 \
    python3-pip \
    curl \
    git \
    build-essential \
    nano \
    unzip && \
  apt clean && \
  apt autoremove --purge

RUN pip3 install pipenv

RUN \
  curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
  unzip awscliv2.zip && \
  ./aws/install && \
  rm -rf ./aws

RUN adduser --uid ${USER_ID} --disabled-password --gecos "" user

RUN \
  git clone --depth=1 https://github.com/tfutils/tfenv.git /home/user/.tfenv && \
  ln -s /home/user/.tfenv/bin/* /usr/local/bin && \
  chown -R user:user /home/user/.tfenv

RUN \
  tfenv install $TF_VERSION && \
  tfenv use $TF_VERSION

USER user
SHELL ["/bin/bash", "--login", "-c"]

RUN \
 curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/${NVM_VERSION}/install.sh | bash && \
 . /home/user/.nvm/nvm.sh && \
 nvm install --lts && \
 nvm use --lts && \
 npm install --global cdktf-cli@${CDKTF_VERSION}

COPY --chmod=755 start.sh /home/user/start.sh
CMD /home/user/start.sh
