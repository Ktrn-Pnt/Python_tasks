#!/usr/bin/env python

import sys
import math
from collections import namedtuple
import numpy as np


def f0():
    number = 3
    if number < 31:
        sys.exit("Numerical limit less than 31")


def f1():
    print("str" + 4)


def f2():
    print(13 / 0)


def f3():
    with np.errstate(invalid='raise'):
        print(np.sqrt(-1))


def f4():
    number = 10000000000
    result = math.exp(number)
    print(result)


def f5():
    value = 100 % 0
    print(value)


def f6():
    assert ('linux' in sys.platform), "This code runs on Linux only."


def f7():
    Marks = namedtuple('Marks', 'Physics Chemistry Math English')
    marks = Marks(90, 85, 95, 100)
    marks.Chemistry = 100
    print(marks)


def f8():
    file = open("TaskPython.txt", 'r')


def f9():
    import request


def f10():
    dictionary = {1: 'a', 2: 'b', 3: 'c'}
    print(dictionary[4])


def f11():
    color = ['red', 'blue', 'green', 'black', 'white', 'orange']
    print(color[6])


def f12():
    ages = {'John': 19, 'Mike': 21, 'Kevin': 20}
    print(ages['Markus'])


def f13():
    priint('Hello, i am solving a problem in python')


def f14():
    print(eval("a * a = a"))


def f15():
    line = int("number")
    print(line)


def f16():
    word = 'café'
    print("ASCII Representation of café: ", word.encode('ascii'))


def check_exception(f, exception):
    try:
        f()
    except exception:
        pass
    else:
        print("Bad luck, no exception caught: %s" % exception)
        sys.exit(1)


check_exception(f0, BaseException)
check_exception(f1, Exception)
check_exception(f2, ArithmeticError)
check_exception(f3, FloatingPointError)
check_exception(f4, OverflowError)
check_exception(f5, ZeroDivisionError)
check_exception(f6, AssertionError)
check_exception(f7, AttributeError)
check_exception(f8, EnvironmentError)
check_exception(f9, ImportError)
check_exception(f10, LookupError)
check_exception(f11, IndexError)
check_exception(f12, KeyError)
check_exception(f13, NameError)
check_exception(f14, SyntaxError)
check_exception(f15, ValueError)
check_exception(f16, UnicodeError)

print("Congratulations, you made it!")
