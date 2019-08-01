#!/bin/bash

sudo pip install protobuf
if [ ! -d $HOME/.protobuf ]; then
    mkdir -p $HOME/.protobuf
fi

outf="$HOME/.protobuf/naming.py"
curl -o $outf https://raw.githubusercontent.com/YuanWenqing/protoplugin/master/src/main/python/naming.py
chmod +x $outf
echo "[done] $outf"
