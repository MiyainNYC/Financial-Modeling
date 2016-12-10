import math

try:
    principal = input("Please enter your principal:\n")
    interest = input("Please enter your interest rate:\n")
    years = input("Please enter number of years:\n")
    print 'Your maturity value is %f' % (principal*((1+interest/12)**(years*12)))
except NameError:
    print 'Please make sure to enter correct values!'