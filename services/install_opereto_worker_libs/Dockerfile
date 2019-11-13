FROM ubuntu:16.04

RUN apt-get -yy update && apt-get -yy upgrade && apt-get install -yy sudo && apt-get install -yy unzip && apt-get install -y git \
&& apt-get install -y build-essential curl && apt-get install -yy python2.7 && apt-get install -yy lsb-release \
&& apt-get install -yy software-properties-common

ENV HOME /root
WORKDIR /root

ENV opereto_workspace "/tmp"
ENV opereto_home "/root/.opereto"
ENV opereto_service_version "default"

COPY . ${opereto_workspace}/

RUN cd $opereto_workspace && python2.7 -u run.py


RUN cd /opt && \
    curl -O https://s3.amazonaws.com/opereto_downloads/opereto-agent-latest.jar && \
    chmod 777 -R *

WORKDIR /opt/opereto-agent-latest

RUN apt-get -yy update && apt-get install -yy openjdk-8-jre && update-alternatives --set java  /usr/lib/jvm/java-8-openjdk-amd64/jre/bin/java

ENV javaParams "-Xms1000m -Xmx1000m"
ENV opereto_host ""
ENV agent_name ""
ENV opereto_user ""
ENV opereto_password ""
ENV log_level="info"

CMD java $javaParams -jar /opt/opereto-agent-latest.jar -host $opereto_host -name $agent_name -u $opereto_user -p $opereto_password -loglevel $log_level -log console