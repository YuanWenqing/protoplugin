#!/bin/bash

LOCALBIN="$HOME/.local/bin"
if [ ! -d $LOCALBIN ]; then
  mkdir -p $LOCALBIN
fi

cd $LOCALBIN
curl https://raw.githubusercontent.com/YuanWenqing/protoplugin/master/src/main/python/sql.py -O
curl https://raw.githubusercontent.com/YuanWenqing/protoplugin/master/src/main/python/proto2sql -O
chmod +x proto2sql
echo """[done] $LOCALBIN/proto2sql

add config to \$HOME/.bashrc :

export PATH=\$PATH:\$HOME/.local/bin
"""

