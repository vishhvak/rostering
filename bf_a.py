"""
BRUTE FORCE with simple/minimal constraints.

You have a dictionary of data consisting of P employees, each having a list of ratings. 

You have shift of a fixed duration of N hours.

You have a list of M units that need to be covered throughout the shift.

Constraints:
- Work time for each controller is assumed to be fixed to 1 hour duties. There are no constraints assumed on break time.
- The number of employees have to be more than the number of units, for takeover. 
- No unit must be left unattended throughout an entire shift.

Goal: Generate a valid roster for the given shift using given data.
"""

import json
import random
import copy
import pprint

data = {
    "A": {
        "ratings": [
            "X",
            "Y",
            "Z"
        ],
    },
    "B": {
        "ratings": [
            "X",
            "Y",
            "Z"
        ],
    },
    "C": {
        "ratings": [
            "X",
            "Y",
            "Z"
        ],
    },
    "D": {
        "ratings": [
            "X",
            "Y"
        ],
    },
    "E": {
        "ratings": [
            "X",
            "Y"
        ],
    },
    "F": {
        "ratings": [
            "X",
            "Y"
        ],
    }
}

shift = 6
employee_list = [i for i in data]
units = ["X", "Y", "Z"]


#Eligible Controllers
#{'X': {'C', 'F', 'D', 'A', 'B', 'E'}, 'Y': {'C', 'F', 'D', 'A', 'B', 'E'}, 'Z': {'C', 'F', 'D', 'A', 'B', 'E'}}


# Filter list of eligible controllers 
eligible_controllers = {}

for unit in units:
    ec = set()
    for j in data:
        if unit in data[j]["ratings"]:
            ec.add(j) 
    eligible_controllers[unit] = ec

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

print("Eligible Controllers\n", eligible_controllers)
print("\n")
# Eligible controllers for given units (changes dynamically)
available_controllers = copy.deepcopy(eligible_controllers)
print("Available controllers before starting.\n", available_controllers, "\n")
# Who's working in what in the given hour
assigned_controllers = {"X": None, "Y": None, "Z": None}
roster = {1: None, 2: None, 3: None, 4: None, 5: None, 6: None}

for i in range(1, 7, 1):

    print("\nHOUR = ", i)
    for unit in units:
        
        ac = available_controllers[unit]
        print("Unit ", unit, ac)
        
        # If no one is assigned to a unit (FIRST HOUR BASICALLY)
        if assigned_controllers[unit] == None:
            # Choose a random controller from eligible available list for given unit
            choice = random.sample(ac, 1)[0]
            print("\nChosen controller", choice)
            # Asssign chosen controller to unit
            assigned_controllers[unit] = choice
            # Discard chosen controller from available list of controllers for all units 
            available_controllers = discard_controller(choice, available_controllers)
            print("\nAvailable controllers", available_controllers)
        
        else:
            # Retrieve currently assigned controller from given unit
            current = assigned_controllers.pop(unit)
            print("\nCurrent controller", current)
            # Choose a random controller from eligible available list for given unit
            choice = random.sample(ac, 1)[0]
            print("\nChosen controller", choice)
            # Assign chosen controller to unit 
            assigned_controllers[unit] = choice
            # Discard chosen controller from available list of controllers for all units
            available_controllers = discard_controller(choice, available_controllers)
            # Restore currently switched controller to available list of controllers
            available_controllers = restore_controller(
                available_controllers, current, eligible_controllers)

            print("\nAvailable controllers", available_controllers)

    print("\nControllers for hour ", i, "=", assigned_controllers)
    roster[i] = assigned_controllers

print("\nFinal roster for 6 hours\n", json.dumps(roster,indent=4))

# TODO
# - Handle Constraints
