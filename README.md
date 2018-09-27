# protoplugin
plugins for ProtocolBuffer.

## How to use

* gradle: see [protobuf-gradle-plugin](https://github.com/google/protobuf-gradle-plugin)

## naming
Naming codegen plugin for Protobuf is used to generate Java code, containing all "naming" constants from protobuf message definitions. The 'naming' here is meant to be the field names in all protobuf messages, excluding enums.

Example: `outer.proto`

~~~protobuf
syntax = "proto3";
package test;

option java_package = "com.example.proto.data";
option java_outer_classname = "Outer";

message Foo {
  int64 id = 1;
  string name = 2;
  repeated float score = 3;
}
~~~

Naming codegen plugin will make a package `naming` under the defined option `java_package` and generate a Java interface `com.example.proto.data.naming.OuterNaming`, including all message namings like below

~~~Java
// Generated by the proto-naming plugin.  DO NOT EDIT!
// source: outer.proto

package com.example.proto.data.naming;

public interface OuterNaming {

  /**
   * @source: test.Foo
   */
  interface FooNaming {
    String ID = "id";
    String NAME = "name";
    String SCORE = "score";
  }
}
~~~

## sql
Sql codegen plugin for Protobuf is used to generate create-table sql template for each message.

Example: 

~~~protobuf
// This is Foo
message Foo {
    string id = 1;
    double double_v = 2;
    repeated int32 int_arr = 3;
    map<string, string> map = 4;

    int64 create_time = 50;
    int64 update_time = 51;
    int64 delete_time = 52;
}
~~~

create-table sql:

~~~sql
-- test.proto.Foo
-- This is Foo
CREATE TABLE IF NOT EXISTS `foo` (
  `id` VARCHAR(32) NOT NULL COMMENT 'this is id',
  `double_v` DECIMAL(20,6) DEFAULT 0,
  `int_arr` TEXT COMMENT '@deprecated',
  `map` TEXT,
  `create_time` DATETIME DEFAULT now(),
  `update_time` DATETIME DEFAULT now() ON UPDATE now(),
  `delete_time` DATETIME DEFAULT NULL,

  PRIMARY KEY (`id`)

) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT 'test.proto.Foo  This is Foo';
~~~

Now you just need to adapt the sql type and limitation of each field and append more necessary key index in this template.

For utility, a easy-used script is produced:
~~~bash
$ ./sql-util.sh

ERROR: ./sql-util.sh <proto_dir> <proto_files> [<msg_names>]

    proto_dir       base dir of proto files'
    proto_files     related path of proto files under <proto_dir>'
                    need quoted if multi'
    msg_names       name of message to print to console, like a,b,c if multi

~~~

To generate the example create-table sql, you can run under project directory:

~~~bash
 ./sql-util.sh src/main/proto message.proto Foo
~~~

## Write A Custom Protobuf Plugin
Tutorials:

English: <https://www.expobrain.net/2015/09/13/create-a-plugin-for-google-protocol-buffer/>

Chinese: <https://tunsuy.github.io/2017/02/20/%E4%B8%BAProtobuf%E7%BC%96%E8%AF%91%E5%99%A8protoc%E7%BC%96%E5%86%99%E6%8F%92%E4%BB%B6/>

