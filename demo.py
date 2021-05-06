#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/5/6 22:27
# @File    : demo.py

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from pprint import pprint

from rule.rule import init_grammar_parser
from rule.rule import EvalTree


def main():
  parser = init_grammar_parser()

  # 规则：买5个包子回来，如果看到西瓜并且西瓜重量大于或等于10，买1个
  rule = """
  if
  ("西瓜" in @"物品列表" and @"西瓜重量" >= 10)
  then "买1个包子" else "买5个包子"
  """
  tree = parser.parse(rule)
  print(tree.pretty())

  variable_dict = {
    "西瓜重量": 10,
    "物品列表": {"包子", "西瓜", "香蕉"},
  }
  tree_evalautor = EvalTree()
  rule_result = tree_evalautor.transform_tree(tree, variable_dict)
  print(rule_result)  # 买1个包子


if __name__ == "__main__":
  main()
