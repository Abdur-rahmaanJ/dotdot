import unittest
from dotdot import Utils

assert Utils.parseValue('..x', memory={'x':'1'}) == '1'
assert Utils.parseFunc('rgb ( x , 4 , 5 )', memory={'x':'1'}) == 'rgb(1,4,5)'
assert Utils.parseShorthand('..y solid black', memory={'y':'10px'}) == '10px solid black'

'''
print(tree.tree)
tree.parse()
print(tree.tree)
tree.output(mode='console')
'''