#!/usr/bin/python3
#_*_encoding:utf-8_*_

# property装饰器
# 作用： 将一个get方法转换为对象的属性。 就是 调用方法改为调用对象
# 使用条件： 必须和属性名一样

# setter方法的装饰器：
# 作用：将一个set方法转换为对象的属性。 就是 a调用方法改为调用对象
# 使用方法：@属性名.setter

class Person:
    def __init__(self,name):
        self._name = name

    # 利用property装饰器将获取name方法转换为获取对象的属性
    @property
    def name(self):
        return self._name

    # 利用property装饰器将设置name方法转换为获取对象的属性
    @name.setter
    def name(self,name):
        self._name = name

class Grasper:
    def __init__(self,conf):
        self._async = 1

    # 利用property装饰器将获取name方法转换为获取对象的属性
    @property
    def async(self):
        return self._async

    # 利用property装饰器将设置name方法转换为获取对象的属性
    @async.setter
    def async(self,async):
        self._async = async        


p = Person('小黑')
print(p.name)   # 原获取 p.name()  , 现 p.name
p.name = '小灰'  # 原设置 p.name('小灰')  ,现 p.name = '小灰'
print(p.name)

grasper = Grasper({})
print(grasper.async)
grasper.async = 0
print(grasper.async)
