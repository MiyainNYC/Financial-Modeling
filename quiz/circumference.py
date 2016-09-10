import math

try:
    radius = input("Please enter an integer:\n")
    print 'circumference is %d' % (math.pi * 2 * radius)
except NameError:
    print 'Please enter an INTEGER!'
