import random
import json

employee_list = ["A", "B", "C", "D", "E"]
units = ["X", "Y", "Z"]
ratings = ["X", "Y", "Z"]

employee_data = {}
# Preparing dummy dataset
for i in employee_list:
    emp_ratings = []
    for j in range(0, random.randint(1, 3)):
        x = random.choice(ratings)
        if x not in emp_ratings:
            emp_ratings.append(x)
    currency = {}
    for k in emp_ratings:
        currency[k] = random.randint(1,10)
    emp_details = {}
    emp_details["ratings"] = emp_ratings
    emp_details["currency"] = currency
    employee_data[i] = emp_details

with open('data.txt', 'w') as outfile:
    json.dump(employee_data, outfile, indent=4)






