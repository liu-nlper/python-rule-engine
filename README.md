# Python Rule System

基于[lark-parser](https://github.com/lark-parser/lark)的简易规则系统。

## 1. 安装lark-parser

    $ pip install lark-parser

## 2. 使用

run demo:

    $ python3 demo.py

### 2.1 自定义Grammar

根据规则需求自定义grammar，语法格式可参考[lark](https://lark-parser.readthedocs.io/en/latest)文档。

示例：

```python
grammar = """
?start: "if" logit "then" value "else" value -> assign

?value: "true"             -> true
      | "false"            -> false
      | string

?logit: and
    | variable                           -> variable_self
    | "!"variable                        -> not_variable_self
    | variable ">" NUMBER                -> bigger
    ...

?and: atom
    | logit "and" logit -> and_op
    | logit "or" logit  -> or_op

?atom: "(" logit ")"

string : ESCAPED_STRING -> string

variable: "@"NAME | "@"string  -> variable

%import common.CNAME -> NAME
%import common.ESCAPED_STRING
%import common.NUMBER
%import common.WS
%ignore WS
"""
```

### 2.2 定义/解析规则

根据所定义的grammar，编写符合语法格式的规则，例如：

```python
from rule.rule import init_grammar_parser

# 定义规则：买5个包子回来，如果看到西瓜并且西瓜重量大于或等于10，买1个
rule = """
if
("西瓜" in @"物品列表" and @"西瓜重量" >= 10)
then "买1个包子" else "买5个包子"
"""

# 构建grammar parser
parser = init_grammar_parser()

# 将规则解析为语法树
tree = parser.parse(rule)
print(tree.pretty())
```

解析得到的tree如下所示：

```
assign
  and_op
    exist_in
      string	"西瓜"
      variable
        string	"物品列表"
    bigger_equal
      variable
        string	"西瓜重量"
      10
  string	"买1个包子"
  string	"买5个包子"
```

### 2.3 匹配规则

以上述grammar和规则为例，前缀为`@`的符号表示变量，可以从程序中实时传入，例如有如下variable：

```python
from rule.rule import EvalTree

variable_dict = {
    "西瓜重量": 10,
    "物品列表": {"包子", "西瓜", "香蕉"},
}
tree_evaluator = EvalTree()
rule_result = tree_evaluator.transform_tree(tree, variable_dict)
print(rule_result)  # 买1个包子
```

## 3. 参考

- lark-parser官方文档：<https://lark-parser.readthedocs.io/en/latest/>
