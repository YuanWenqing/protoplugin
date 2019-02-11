#!/usr/bin/python

import sys
import os

from google.protobuf.compiler import plugin_pb2 as plugin
from google.protobuf.descriptor_pb2 import FieldDescriptorProto


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
    formatted += padding + '<p>\n'
    return formatted

def padding(lines, prefix):
    padded = ''
    for line in lines.split('\n'):
        if line.strip() != '':
            padded += prefix + line
        padded += '\n'
    return padded


class FileNamingGenerator:
    def __init__(self, javaPkg, proto):
        self.proto = proto
        self.javaPkg = javaPkg
        self.javaOuterCls = proto.options.java_outer_classname + 'Naming'

    def get_filename(self):
        path = self.javaPkg.replace('.', os.path.sep)
        fn = self.javaOuterCls + '.java'
        return os.path.join(path, fn)

    def head(self):
        return """/* Generated by the proto-naming plugin.  DO NOT EDIT! */

package %s;

/**
 * file: %s
 */
public interface %s {\n""" % (self.javaPkg, self.proto.name, self.javaOuterCls)

    def tail(self):
        return "}\n"

    def body(self):
        code = ''
        for msgIdx in range(len(self.proto.message_type)):
            code += self.handle_message(msgIdx) + '\n'
        # return padding(code, '  ')
        return ''

    def handle_message(self, msg_idx):
        code = "/**\n"
        comment = find_msg_comment(self.proto.source_code_info.location, msg_idx)
        comment = format_comment(comment, ' * ')
        code += comment

        msg = self.proto.message_type[msg_idx]
        full_name = self.proto.package + '.' + msg.name
        code += " * proto: %s\n" % full_name
        code += " */\n"

        if msg.options.deprecated:
            code += '@java.lang.Deprecated\n'

        code += 'String %s = "%s";' % (msg.name.upper(), msg.name)

        return code


class MessageNamingGenerator:
    def __init__(self, javaPkg, proto, msg_idx):
        self.proto = proto
        self.javaPkg = javaPkg
        self.msg_idx = msg_idx
        self.msg = self.proto.message_type[msg_idx]

    def get_filename(self):
        path = self.javaPkg.replace('.', os.path.sep)
        fn = '%sNaming.java' % (self.msg.name,)
        return os.path.join(path, fn)

    def head(self):
        return """/* Generated by the proto-naming plugin.  DO NOT EDIT! */

package %s;

""" % (self.javaPkg,)

    def body(self):
        code = "/**\n"
        comment = find_msg_comment(self.proto.source_code_info.location, self.msg_idx)
        comment = format_comment(comment, ' * ')
        code += comment

        full_name = self.proto.package + '.' + self.msg.name
        code += " * proto: %s\n" % full_name
        code += " */\n"

        if self.msg.options.deprecated:
            code += '@java.lang.Deprecated\n'

        code += "public interface %sNaming {\n" % self.msg.name
        for fieldIdx in range(len(self.msg.field)):
            code += self.handle_message_field(fieldIdx)
        code += "}\n"

        return code

    def handle_message_field(self, field_idx):
        code = "  /**\n"
        comment = find_field_comment(self.proto.source_code_info.location, self.msg_idx, field_idx)
        comment = format_comment(comment, '   * ')
        code += comment

        field = self.msg.field[field_idx]
        type_name = FieldDescriptorProto.Type.Name(field.type)
        if field.type_name  != '':
            type_name += ": " + field.type_name
        code += "   * %s\n" % type_name
        code += "   */\n"

        if field.options.deprecated:
            code += '  @java.lang.Deprecated\n'

        code += '  String %s = "%s";\n' % (field.name.upper(), field.name)
        return code


# class NamingGenerator:
#     FileTemplate = """/* Generated by the proto-naming plugin.  DO NOT EDIT! */

# package %s;

# /**
#  * file: %s
#  */
# public interface %s {
# %s
# }
# """
#     MsgTemplate = """
#   /**
# %s   * proto: %s
#    */%s
#   interface %sNaming {
# %s
#   }
# """
#     FieldTemplate = '    String %s = "%s";\n'

#     def __init__(self, proto):
#         self.proto = proto
#         self.javaPkg = '%s.naming' % proto.options.java_package
#         self.javaOuterCls = proto.options.java_outer_classname + 'Naming'

#     def generate(self):
#         code = ''
#         for msgIdx in range(len(self.proto.message_type)):
#             code += self.handle_message(msgIdx)
#         return NamingGenerator.FileTemplate % (self.javaPkg, self.proto.name, self.javaOuterCls, code)

#     def handle_message(self, msg_idx):
#         msg = self.proto.message_type[msg_idx]
#         full_name = self.proto.package + '.' + msg.name
#         annotation = ''
#         if msg.options.deprecated:
#             annotation = '\n  @java.lang.Deprecated'
#         field_code = ''
#         for fieldIdx in range(len(msg.field)):
#             field_code += self.handle_message_field(msg_idx, fieldIdx)
#         comment = find_msg_comment(self.proto.source_code_info.location, msg_idx)
#         comment = format_comment(comment, '   * ')
#         return NamingGenerator.MsgTemplate % (comment, full_name, annotation, msg.name, field_code)

#     def handle_message_field(self, msg_idx, field_idx):
#         msg = self.proto.message_type[msg_idx]
#         field = msg.field[field_idx]
#         code = ''
#         if field.options.deprecated:
#             code = '    @java.lang.Deprecated\n'
#         code += NamingGenerator.FieldTemplate % (field.name.upper(), field.name)
#         comment = find_field_comment(self.proto.source_code_info.location, msg_idx, field_idx)
#         comment = format_comment(comment, '     * ')
#         if comment != '':
#             comment = '    /**\n%s     */\n' % comment
#             code = comment + code
#         return code


def parse_parameter(parameter):
    opts = {}
    for part in parameter.split(','):
        pos = part.find('=')
        if pos < 0:
            opts[part] = None
        else:
            opts[part[0:pos]] = part[pos+1:]
    return opts


def generate_code(req, resp):
    n2f = index_proto(req.proto_file)
    opts = parse_parameter(req.parameter)

    for filename in req.file_to_generate:
        proto = n2f[filename]
        if len(proto.message_type) == 0:
            continue

        javaPkg = '%s.naming' % proto.options.java_package
        if 'java_package' in opts:
            javaPkg = opts['java_package']
        if proto.options.java_multiple_files:
            for msgIdx in range(len(proto.message_type)):
                generator = MessageNamingGenerator(javaPkg, proto, msgIdx)
                outf = resp.file.add()
                outf.name = generator.get_filename()
                outf.content = generator.head() + generator.body()
        else:
            file_naming_generator = FileNamingGenerator(javaPkg, proto)
            outf = resp.file.add()
            outf.name = file_naming_generator.get_filename()
            content = file_naming_generator.head() + file_naming_generator.body()
            for msgIdx in range(len(proto.message_type)):
                msg_cnt = MessageNamingGenerator(javaPkg, proto, msgIdx).body()
                content += padding(msg_cnt, '  ')
            content += file_naming_generator.tail()
            outf.content = content


        # generator = NamingGenerator(proto)
        # out_f = resp.file.add()
        # path = generator.javaPkg.replace('.', os.path.sep)
        # fn = generator.javaOuterCls + '.java'
        # out_f.name = os.path.join(path, fn)
        # out_f.content = generator.generate()


if __name__ == '__main__':
    # Read request message from stdin
    data = sys.stdin.read()

    # Parse request
    request = plugin.CodeGeneratorRequest()
    request.ParseFromString(data)

    # Create response
    response = plugin.CodeGeneratorResponse()

    # Generate code
    generate_code(request, response)

    # Serialise response message
    output = response.SerializeToString()

    # Write to stdout
    sys.stdout.write(output)
