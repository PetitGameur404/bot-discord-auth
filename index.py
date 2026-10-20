import json

with open('db.json', 'r') as f:
    d = json.load(f)

# print(d)

liste = d["utilisateurs"]

trouve = False
email = input("tape email :")

for user in liste:
    if email == user["mail"]:
        trouve = True

if trouve:
        print("tu est dans la liste")
else:
    print("pas acces")