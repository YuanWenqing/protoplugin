#!/bin/bash

if [ $# -lt 2 ]; then
  echo """ERROR: $0 <proto_dir> <proto_files> [<msg_names>]

    proto_dir       base dir of proto files'
    proto_files     related path of proto files under <proto_dir>'
                    need quoted if multi'
    msg_names       name of message to print to console, like a,b,c if multi
"""
  exit 1
fi

PROTO_DIR=$1
PROTO_FILE=$2
MSG_NAME=""
if [ $# -eq 3 ]; then
  MSG_NAME=$3
fi

OUT_DIR=./sql
if [ ! -d $OUT_DIR ]; then
    mkdir -p $OUT_DIR
fi

SCRIPT_DIR=$(dirname $0)
SQL_PLUGIN=$SCRIPT_DIR/src/main/python/sql.py

protoc \
    --proto_path=$PROTO_DIR \
    --plugin=protoc-gen-sql=$SQL_PLUGIN \
    --sql_out=$MSG_NAME:$OUT_DIR \
    $PROTO_FILE

