#!/bin/bash

OS=$(lsb_release -si)
if [ -f /etc/redhat-release ];then
    OSREL=$(cat /etc/redhat-release)
elif [ -f /etc/os-release ];then
    OSREL=$(cat /etc/os-release)
fi


if [[ $OS == *"buntu"* ]]; then
  os_platform="ubuntu"
elif [[ $OS == *"RedHat"* ]]; then
  os_platform="rh"
elif [[ $OS == *"entos"* ]]; then
  os_platform="centos"
elif [[ $OSREL == *"Red Hat"* ]]; then
  os_platform="rh"
elif [[ $OSREL == *"entos"* ]]; then
  os_platform="centos"
elif [[ $OSREL == *"CentOS"* ]]; then
  os_platform="centos"
elif [[ $OSREL == *"buntu"* ]]; then
  os_platform="ubuntu"
elif [[ $OSREL == *"Amazon"* ]]; then
  os_platform="rh"
fi

if [ -z "$os_platform" ]; then
    echo "Cannot identify OS platform."
    exit 1;
fi


if [ $os_platform == "ubuntu" ]; then

    if [[ $OSREL != *"Trusty"* ]]; then
        sudo apt-get install -y python2.7
        sudo sed -i 's/^mesg n || true$/tty -s \&\& mesg n/g' /root/.profile
    else
        echo ""
    fi
else
    echo "Installing opereto lib on $os_platform. Assuming that Python2.7 is installed"
fi

python2.7 -u run.py








