import sys

sum = 0

for i in range(1, sys.maxint):
    sum += ((-1) ** (i + 1) / i) * (2 / 3) ** i
    print sum
    if thereIsAReasonToBreak(i):
        break
