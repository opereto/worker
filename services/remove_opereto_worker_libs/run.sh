#!/bin/bash
LIBS=$opereto_home/operetovenv
sudo -iEn rm -rf $LIBS
if [ $? -eq 0 ]; then
    echo "Opereto worker libraries [$LIBS] removed."
    python2.7 -u run.py
    exit 0
else
    echo "Failed to remove. Please remove $LIBS manually"
    exit 2;
fi






