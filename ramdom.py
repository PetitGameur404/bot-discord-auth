import secrets

code = "".join(str(n) for n in secrets.SystemRandom().sample(range(10), 4))
print(code)