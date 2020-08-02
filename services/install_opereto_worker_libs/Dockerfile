FROM ubuntu:16.04

ENV HOME /root
ENV opereto_workspace "/tmp"
ENV opereto_home "/root/.opereto"
ENV opereto_service_version "default"
ENV javaParams "-Xms1000m -Xmx1000m"
ENV log_level="info"
ENV opereto_host ""
ENV opereto_token ""
ENV agent_name ""

WORKDIR /root

RUN apt-get -yy update --fix-missing && apt-get -yy upgrade && apt-get install -yy sudo
RUN apt-get install -yy unzip && apt-get install -y git \
&& apt-get install -y build-essential curl && apt-get install -yy python2.7 && apt-get install -yy lsb-release \
&& apt-get install -yy software-properties-common

RUN curl -LO https://storage.googleapis.com/kubernetes-release/release/v1.17.0/bin/linux/amd64/kubectl && chmod +x ./kubectl && sudo mv ./kubectl /usr/local/bin/kubectl

COPY . ${opereto_workspace}/

RUN cd $opereto_workspace && python2.7 -u run.py

RUN cd /opt && \
    curl -O https://s3.amazonaws.com/opereto_downloads/3.0.110/opereto-agent-latest.jar && \
    chmod 777 -R *

WORKDIR /opt/opereto-agent-latest

RUN apt-get -yy update && apt-get install -yy openjdk-8-jre && update-alternatives --set java  /usr/lib/jvm/java-8-openjdk-amd64/jre/bin/java


CMD java $javaParams -jar /opt/opereto-agent-latest.jar -host $opereto_host -name $agent_name -token $opereto_token -loglevel $log_level -log console

