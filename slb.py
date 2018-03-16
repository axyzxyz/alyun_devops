#! /usr/local/bin python3.6
"""
@Time    : 2018/3/11 2:04
@Author  : ysj
@Site    :
@File    : slb.py
@Software: PyCharm
"""
class A:
    def __init__(self, a=2, b=3):
        self.a = a
        self.x = b


class B(A):
    a = 'x'
    def __init__(self):
        super().__init__()
        self.a = 'z'


b = B()
print(b.a, b.x)