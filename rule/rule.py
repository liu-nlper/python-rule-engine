#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/5/6 22:24
# @File    : rule.py
"""
  Rule.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import re
from lark import Lark
from lark import Token
from lark import Transformer


_grammar = """
?start: "if" logit "then" value "else" value -> assign

?value: "true"             -> true
      | "false"            -> false
      | string

?logit: and
    | variable                           -> variable_self
    | "!"variable                        -> not_variable_self
    | variable ">" NUMBER                -> bigger
    | variable ">=" NUMBER               -> bigger_equal
    | variable "<" NUMBER                -> smaller
    | variable "<=" NUMBER               -> smaller_equal
    | variable "==" (NUMBER | string)    -> equal
    | variable "!=" (NUMBER | string)    -> not_equal
    | string "in" variable               -> exist_in        // 实际使用正则匹配
    | string "!in" variable              -> not_exist_in    // 实际使用正则匹配

?and: atom
    | logit "and" logit -> and_op
    | logit "or" logit  -> or_op

?atom: "(" logit ")"

string : ESCAPED_STRING -> string

// 实际会替换为对应的变量
variable: "@"NAME | "@"string  -> variable

%import common.CNAME -> NAME
%import common.ESCAPED_STRING
%import common.NUMBER
%import common.WS
%ignore WS
"""


def init_grammar_parser():
  parser = Lark(_grammar, parser='lalr', debug=True)
  return parser


class EvalTree(Transformer):

  def __init__(self, variable_dict=None):
    super(EvalTree, self).__init__()
    if variable_dict is None:
      variable_dict = {}
    self.variable_dict = variable_dict

  def transform_tree(self, tree, variable_dict):
    self.variable_dict = variable_dict
    return self._transform_tree(tree)

  def _token2node(self, token):
    if not isinstance(token, Token):
      return token
    token_value = token.value
    if token.type == "NUMBER":
      token_value = float(token.value)
    return token_value

  def true(self, args):
    return True

  def false(self, args):
    return False

  def string(self, args):
    return eval(self._token2node(args[0]))

  def variable(self, args):
    variable_name = self._token2node(args[0])
    return self.variable_dict.get(variable_name, None)

  def variable_self(self, args):
    variable_value = self._token2node(args[0])
    if variable_value is None or not variable_value:
      return False
    return True

  def not_variable_self(self, args):
    variable_value = self._token2node(args[0])
    if variable_value is None or not variable_value:
      return True
    return False

  def bigger(self, args):
    arg_0 = self._token2node(args[0])
    arg_1 = self._token2node(args[1])
    if arg_0 is not None and arg_0 > arg_1:
      return True
    return False

  def bigger_equal(self, args):
    arg_0 = self._token2node(args[0])
    arg_1 = self._token2node(args[1])
    if arg_0 is not None and arg_0 >= arg_1:
      return True
    return False

  def smaller(self, args):
    arg_0 = self._token2node(args[0])
    arg_1 = self._token2node(args[1])
    if arg_0 is not None and arg_0 < arg_1:
      return True
    return False

  def smaller_equal(self, args):
    arg_0 = self._token2node(args[0])
    arg_1 = self._token2node(args[1])
    if arg_0 is not None and arg_0 <= arg_1:
      return True
    return False

  def equal(self, args):
    arg_0 = self._token2node(args[0])
    arg_1 = self._token2node(args[1])
    if arg_0 is not None and arg_0 == arg_1:
      return True
    return False

  def not_equal(self, args):
    arg_0 = self._token2node(args[0])
    arg_1 = self._token2node(args[1])
    if arg_0 is not None and arg_0 != arg_1:
      return True
    return False

  def exist_in(self, args):
    arg_0 = self._token2node(args[0])
    arg_1 = self._token2node(args[1])
    if isinstance(arg_1, str):
      if re.search(arg_0, arg_1):
        return True
    else:
      if arg_1 is not None and arg_0 in arg_1:
        return True
    return False

  def not_exist_in(self, args):
    arg_0 = self._token2node(args[0])
    arg_1 = self._token2node(args[1])
    if isinstance(arg_1, str):
      if not re.search(arg_0, arg_1):
        return True
    else:
      if arg_1 is None or arg_0 not in arg_1:
        return True
    return False

  def and_op(self, args):
    return args[0] and args[1]

  def or_op(self, args):
    return args[0] or args[1]

  def NAME(self, args):
    return args.value

  def assign(self, args):
    if args[0]:
      return args[1]
    return args[2]
