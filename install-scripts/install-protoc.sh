#!/bin/bash

PROTOC_VERSION=3.7.0
PROTOC_HOME=/data/install/protoc

if [ $# -gt 0 ]; then
    PROTOC_VERSION=$1
fi

if [ -d $PROTOC_HOME ]; then
    mkdir -p $PROTOC_HOME
fi

cd /data/application
curl -OL "https://github.com/protocolbuffers/protobuf/releases/download/v${PROTOC_VERSION}/protoc-${PROTOC_VERSION}-linux-x86_64.zip"
unzip -o protoc-${PROTOC_VERSION}-linux-x86_64.zip -d /data/install/protoc/${PROTOC_VERSION}
ln -sf $PROTOC_HOME/$PROTOC_VERSION $PROTOC_HOME/latest
if [ ! -f /data/bin/protoc ]; then
    ln -s $PROTOC_HOME/latest/bin/protoc /data/bin/protoc
fi

echo "[done] protoc: $PROTOC_VERSION"
