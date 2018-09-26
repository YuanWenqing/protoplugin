OUT_DIR=./gen
if [ ! -d $OUT_DIR ]; then
    mkdir -p $OUT_DIR
fi

PROTO_DIR=./src/main/proto

protoc \
    --proto_path=$PROTO_DIR \
    --plugin=protoc-gen-naming=src/main/python/naming.py \
    --naming_out=$OUT_DIR \
    message.proto

