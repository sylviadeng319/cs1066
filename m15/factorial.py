### m15/factorial.py

ans = input("What n would you like to compute the factorial of? ")
n = int(ans)

fact = 1
for i in range(1, n + 1):
    fact *= i

print(f"The factorial of {n} is {fact}")
