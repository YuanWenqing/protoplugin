#!/usr/bin/python

import sys, os

from google.protobuf.compiler import plugin_pb2 as plugin
from google.protobuf.descriptor_pb2 import DescriptorProto, EnumDescriptorProto

from utils import *


class NamingFormatter:
  FileTemplate = '''// Generated by the proto-naming plugin.  DO NOT EDIT!
// source: %s

package %s;

public interface %s {
%s
}
'''
  MsgTemplate = '''
  /**
%s   * @source: %s
   */%s
  interface %sNaming {
%s
  }
'''
  FieldTemplate = '    String %s = "%s";\n'

  def __init__(self, proto):
    self.proto = proto
    self.javaPkg = '%s.naming' % proto.options.java_package
    self.javaOuterCls = proto.options.java_outer_classname + 'Naming'

  def generate_code(self):
    code = ''
    for msgIdx in range(len(self.proto.message_type)):
      code += self.generate_msg(msgIdx)
    return NamingFormatter.FileTemplate % (self.proto.name, self.javaPkg, self.javaOuterCls, code)

  def generate_msg(self, msgIdx):
    msg = self.proto.message_type[msgIdx]
    fullName = self.proto.package + '.' + msg.name
    annotation = ''
    if msg.options.deprecated:
      annotation = '\n  @java.lang.Deprecated'
    fieldCode = ''
    for fieldIdx in range(len(msg.field)):
      fieldCode += self.generate_field(msgIdx, fieldIdx)
    comment = findMsgComment(self.proto.source_code_info.location, msgIdx)
    comment = formatComment(comment, '   * ')
    return NamingFormatter.MsgTemplate % (comment, fullName, annotation, msg.name, fieldCode)

  def generate_field(self, msgIdx, fieldIdx):
    msg = self.proto.message_type[msgIdx]
    field = msg.field[fieldIdx]
    code = ''
    if field.options.deprecated:
      code = '    @java.lang.Deprecated\n'
    code += NamingFormatter.FieldTemplate % (field.name.upper(), field.name)
    comment = findFieldComment(self.proto.source_code_info.location, msgIdx, fieldIdx)
    comment = formatComment(comment, '     * ')
    if comment != '':
      comment = '    /**\n%s     */\n' % comment
      code = comment + code
    return code


def generate_code(request, response):
  n2f = index_proto(request.proto_file)

  for filename in request.file_to_generate:
    proto = n2f[filename]

    formatter = NamingFormatter(proto)
    outf = response.file.add()
    path = formatter.javaPkg.replace('.', os.path.sep)
    fn = formatter.javaOuterCls + '.java'
    outf.name = os.path.join(path, fn)
    outf.content = formatter.generate_code()


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
