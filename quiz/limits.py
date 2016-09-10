from sympy import limit,oo,Symbol

x = Symbol('x')

limit((1+1/x)**(2*x),x,oo)