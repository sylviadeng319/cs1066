### m15/area.py

import math

ans = input("What is the radius of your circle? ")

radius = float(ans)
tmp = radius ** 2
area = math.pi * tmp

print(f"The area of a circle with radius {radius} is {area}")
