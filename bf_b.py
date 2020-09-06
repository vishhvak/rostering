"""
BRUTE FORCE

You have a dataframe with employee, ratings, currency_rating, [preferences].

You have shift(s) of a fixed duration that cover an entire day of 24 hours.

You have a list of units that need to be covered throughout the shift(s)

Each controller work for a maximum duration of 2 hours, minimum duration of 30 minutes.

Each controller needs a minimum 30 minute break after finishing one duty. 

The number of employees have to be more than the number of units. 

No unit must be left unattended throughout an entire shift.

What do we want to minimize?
- Overall currency of employees (i.e reduce time remaining to work for them in total?)


class Unit:
    def __init__(self, name, assigned_controller):
        self.name = name
        self.assigned_controller = assigned_controller
    
    def set_controller(controller):
        self.assigned_controller = controller

    def get_controller():
        return self.assigned_controller
"""

import json
import random
import copy

# with open('data.txt') as json_file:
#     data = json.load(json_file)

data = {
    "A": {
        "ratings": [
            "Z",
            "X"
        ],
        "currency": {
            "Z": 6,
            "X": 3
        }
    },
    "B": {
        "ratings": [
            "Y",
            "Z"
        ],
        "currency": {
            "Y": 3,
            "Z": 4
        }
    },
    "C": {
        "ratings": [
            "X",
            "Y"
        ],
        "currency": {
            "X": 3,
            "Y": 1
        }
    },
    "D": {
        "ratings": [
            "Z"
        ],
        "currency": {
            "Z": 5
        }
    },
    "E": {
        "ratings": [
            "Y"
        ],
        "currency": {
            "Y": 2
        }
    },
    "F": {
        "ratings": [
            "X"
        ],
        "currency": {
            "X": 4
        }
    }
}

shift = 6
employee_list = ["A", "B", "C", "D", "E", "F"]
units = ["X", "Y", "Z"]

max_work_time = 2
min_work_time = 0.5
break_time = 0.5

eligible_controllers = {}


for i in units:
    ec = set()
    for j in data:
        if i in data[j]["ratings"]:
            ec.add(j)  # Include , data[j]["currency"][i] later
    eligible_controllers[i] = ec


def getKeysByValue(dictOfElements, valueToFind):
    listOfKeys = list()
    listOfItems = dictOfElements.items()
    for item in listOfItems:
        for j in item[1]:
            if j == valueToFind:
                listOfKeys.append(item[0])
    return listOfKeys


def restore_controller(ac, current, ec):
    #print("Restore Worker elements", ec, current)
    keys = getKeysByValue(ec, current)
    print("\nKeys to restore\n", keys)
    for key in keys:
        ac[key].add(current)
    return ac

def discard_controller(clr, ac):
    for k in ac.values():
        k.discard(clr)
    return ac

# ac = {"X":{"A","B"}}
# unit = "X"
# data
# currency_list = [("A",6),("B",8)]

def get_sorted_currency_list(ac, unit, data):
    currency_list = []
    for emp in ac:
        currency_list.append((emp, data[emp]["currency"][unit]))
        
    


print("Eligible Controllers\n", eligible_controllers)
print("\n")
# Eligible controllers for given units (changes dynamically)
available_controllers = copy.deepcopy(eligible_controllers)
print("Available controllers before starting.\n", available_controllers, "\n")
# Who's working in what in the given hour
assigned_controllers = {"X": None, "Y": None, "Z": None}
roster = {"1": None, "2": None, "3": None, "4": None, "5": None, "6": None}

for i in range(1, 7, 1):
    print("\nHOUR = ", i)
    for unit in units:
        ac = available_controllers[unit]
        print("Unit ", unit, ac)
        if assigned_controllers[unit] == None:
            print("\nChosen controller", choice)
            assigned_controllers[unit] = choice
            available_controllers = discard_controller(choice, available_controllers)
            print("\nAvailable controllers", available_controllers)
        else:
            current = assigned_controllers.pop(unit)
            print("\nCurrent controller", current)
            choice = random.sample(ac, 1)[0]
            print("\nChosen controller", choice)
            assigned_controllers[unit] = choice
            available_controllers = discard_controller(choice, available_controllers)
            available_controllers = restore_controller(
                available_controllers, current, eligible_controllers)
            print("\nAvailable controllers", available_controllers)
    print("\nControllers for hour ", i, "=", assigned_controllers)
    roster[i] = assigned_controllers

print("\nFinal roster for 6 hours\n", roster)

# TODO
# - Handle Constraints
