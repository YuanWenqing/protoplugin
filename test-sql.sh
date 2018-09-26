OUT_DIR=./gen/sql
if [ ! -d $OUT_DIR ]; then
    mkdir -p $OUT_DIR
fi

PROTO_DIR=./src/main/proto

protoc \
    --proto_path=$PROTO_DIR \
    --plugin=protoc-gen-sql=src/main/python/sql.py \
    --sql_out=$OUT_DIR \
    message.proto

