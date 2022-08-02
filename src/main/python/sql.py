#!/usr/bin/env python
# coding: utf8

import sys

from google.protobuf.compiler import plugin_pb2 as plugin
from google.protobuf.descriptor_pb2 import FieldDescriptorProto as fdp


def index_proto(proto_files):
    n2f = dict()
    for proto_file in proto_files:
        n2f[proto_file.name] = proto_file

    return n2f


def find_msg_comment(locations, msg_idx):
    return find_comment(locations, [4, msg_idx])


def find_field_comment(locations, msg_idx, field_idx):
    return find_comment(locations, [4, msg_idx, 2, field_idx])


def find_comment(locations, path):
    finds = find_location(locations, path)
    s = ''
    for l in finds:
        s += l.leading_comments or ''
        s += l.trailing_comments or ''
    return s


def find_location(locations, path):
    """
    path: path of comment, see https://github.com/google/protobuf/blob/master/src/google/protobuf/descriptor.proto
    examples paths:
    [4, m] - message comments, m: msgIdx in proto from 0
    [4, m, 2, f] - field comments in message, f: fieldIdx in message from 0
    [6, s] - service comments, s: svcIdx in proto from 0
    [6, s, 2, r] - rpc comments in service, r: rpc method def in service from 0
    """
    finds = []
    for l in locations:
        if l.path != path:
            continue
        finds.append(l)
    return finds


def format_comment(comments, padding):
    if not comments or len(comments) == 0:
        return ''
    formatted = ''
    for line in comments.split('\n'):
        line = line.strip()
        if line != '':
            formatted += padding + line + '\n'
    return formatted


def underscore(name):
    new_name = ''
    for c in name:
        if c == c.upper():
            if len(new_name) != 0:
                new_name += '_'
        new_name += c.lower()
    return new_name


class SqlGenerator:
    FileTemplate = """-- Generated by the protoc-gen-sql plugin.  DO NOT EDIT!
-- file: %s

%s
"""
    MsgTemplate = """%s
CREATE TABLE IF NOT EXISTS `%s` (
%s
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT '%s';
"""

    def __init__(self, proto, msg_filter):
        self.proto = proto
        self.msg_filter = msg_filter

    def generate(self):
        code = ''
        for msgIdx in range(len(self.proto.message_type)):
            code += self.handle_message(msgIdx) + "\n"
        return SqlGenerator.FileTemplate % (self.proto.name, code)

    def handle_message(self, msg_idx):
        msg = self.proto.message_type[msg_idx]
        full_name = self.proto.package + '.' + msg.name
        table_name = underscore(msg.name)

        comment = full_name + "\n"
        if msg.options.deprecated:
            comment += "@deprecated\n"
        comment += find_msg_comment(self.proto.source_code_info.location, msg_idx)
        comment_line = comment.strip().replace("\n", " ")
        table_comment = format_comment(comment, '-- ').strip()

        lines = []
        # field
        for field_idx in range(len(msg.field)):
            field_line = self.handle_message_field(msg_idx, field_idx)
            lines.append(field_line)
        lines.append("")
        # index
        for field in msg.field:
            if field.name == 'id':
                lines.append("PRIMARY KEY (`id`)")

        table_code = ""
        for idx in range(len(lines)):
            line = lines[idx]
            if line != "":
                table_code += "  " + line
                if idx + 1 < len(lines):
                    table_code += ","
            table_code += "\n"

        msg_code = SqlGenerator.MsgTemplate % (table_comment, table_name, table_code, comment_line)
        if msg.name in self.msg_filter:
            sys.stderr.write(msg_code)
            sys.stderr.write("\n")
        return msg_code

    def handle_message_field(self, msg_idx, field_idx):
        msg = self.proto.message_type[msg_idx]
        field = msg.field[field_idx]
        code = "`%s` " % field.name

        if field.label == fdp.LABEL_REPEATED:
            code += "TEXT"
        elif field.name == 'create_time':
            code += "TIMESTAMP DEFAULT now()"
        elif field.name == 'update_time':
            code += "TIMESTAMP DEFAULT now() ON UPDATE now()"
        elif field.type_name.endswith('google.protobuf.Timestamp'):
            # time field
            code += "TIMESTAMP NULL"
        elif field.name == 'id':
            if field.type == fdp.TYPE_INT64:
                code += "BIGINT(20) NOT NULL AUTO_INCREMENT"
            else:
                code += "VARCHAR(32) NOT NULL"
        elif field.type == fdp.TYPE_INT64:
            code += "BIGINT(20) DEFAULT 0"
        elif field.type == fdp.TYPE_INT32:
            code += "INT(10) DEFAULT 0"
        elif field.type == fdp.TYPE_DOUBLE:
            code += "DECIMAL(20,6) DEFAULT 0"
        elif field.type == fdp.TYPE_FLOAT:
            code += "DECIMAL(12,4) DEFAULT 0"
        elif field.type == fdp.TYPE_BOOL:
            code += "TINYINT(1) DEFAULT 0"
        elif field.type == fdp.TYPE_ENUM:
            code += "TINYINT(2) DEFAULT 0"
        elif field.type == fdp.TYPE_STRING:
            if field.name == 'url' or field.name.endswith("_url"):
                code += "TEXT"
            else:
                code += "VARCHAR(100) DEFAULT ''"
        elif field.type == fdp.TYPE_MESSAGE:
            code += "TEXT"
        else:
            sys.stderr.write("! unhandled field: %s.%s" % (msg.name, field.name))

        comment = find_field_comment(self.proto.source_code_info.location, msg_idx, field_idx)
        comment_line = comment.strip().replace("\n", " ")
        if field.options.deprecated:
            comment_line = "@deprecated " + comment_line
        comment_line = comment_line.strip()
        if comment_line != "":
            code = "%s COMMENT '%s'" % (code, comment_line)
        return code


def generate_sql(req, resp):
    n2f = index_proto(req.proto_file)

    msg_filter = []
    if req.parameter:
        msg_filter = [name.strip() for name in req.parameter.split(',')]

    for filename in req.file_to_generate:
        proto = n2f[filename]
        if len(proto.message_type) == 0:
            continue

        generator = SqlGenerator(proto, msg_filter)
        out_f = resp.file.add()
        out_f.name = filename.replace(".proto", ".sql")
        out_f.content = generator.generate()


if __name__ == '__main__':
    # Read request message from stdin
    data = sys.stdin.read()

    # Parse request
    request = plugin.CodeGeneratorRequest()
    request.ParseFromString(data)

    # Create response
    response = plugin.CodeGeneratorResponse()

    # Generate code
    generate_sql(request, response)

    # Serialise response message
    output = response.SerializeToString()

    # Write to stdout
    sys.stdout.write(output)
