
import numpy as np
import copy
import json
import random
"""
    Constraints:

    Each slot of work time is 30 minutes.

    Shift duration is fixed as N. 
    Number of employees is fixed as M.
    An atomic time slot t = 30 minutes. 
    Total number of time slots = shift_duration/t => T = N/t = N/30

    Total number of controllers >= units (Controllers can have multiple ratings)
    => Number of eligible controllers for a given unit > 1.

    Minimum_work_time = 30 minutes
    Maximum_work_time = 120 minutes (2 hours)

    After every duty (whether 30 min, 1 hr, 1.5hrs or 2hrs), 
    a controller needs a mandatory break of 30 minutes (i.e 1 time slot)
    => No controller can change positions in consecutive time slots.

    Sort units by key = number of eligible controllers, in ascending order. 
    Units with lesser eligible controllers tend to produce leaf nodes, hence are better dealt with earlier in the roster.

    Preference is given to the controller with higher time_remaining to work in a given unit to maintain his rating.

    Currency in this program represents time remaining to work in given unit.

"""

"""
    WORKFLOW:
        1. Create Units, Controllers.
        2. Create Roster object.
        3. Call create_roster
        4. Call print_roster if no errors.
    
    EXPLANATION:
        1. Loop over shift duration in atomic timeslots of break_time 
        2. For each timeslot, loop over the units that are free, i.e the units that need to be taken over based on existing assignments.
        3. Each assignment to a unit takes a controller. A controller is fixed assign_next_at based on his currency value, whenever he gets 
        assigned to a unit. This is used to filter free units in the given timeslot. If assign_next_at == current_timeslot, unit is a free unit.
        4. Loop over free units in given timeslot and fetch the most suitable controller from the list of available controllers for the unit.
        This is done based on currency values of controllers, they are sorted in decreasing order of currency value. 
        5. The controller with highest time_remaining (currency) is assigned to unit, takesover existing controller, and assign_next_at is set,
        is_working = True
        6. Existing contoller - is_working = False, last_work_time is set as current time_slot (the timeslot he is taken over)
        7. To check for break_time constraints, we subtract current time_slot - last_work_time => This tells us how long it has been since
        he has last worked in the roster. If this value > 0.5 (30 min), he is eligible to work.
        8. These steps repeat and the loop stops once the entire shift has been covered or if there is a non-availability of controllers for units.

    If no. of controllers = 2 * no. of units, the output has errors sometimes, sometimes works.
    Based on testing, with 7 units, 20 controllers - roster seems to work fine.
    In real time scenario, we would be having way more controllers than no. of units so this algorithm will not fail in most cases.

    Backtracking and Look Ahead is yet to be implemented. 
"""


class Roster:
    def __init__(self, units, controllers, shift_duration):
        self.units = units
        self.eligible_controllers = self.set_eligible_controllers(controllers)
        self.shift_duration = shift_duration
        self.time_slot = 0
        self.required_break_time = 0.5
        self.roster = {}

    def validate_data(self):
        """
            Validates data based on conditions.
            1. Number of controllers for each unit > 1.
            2. More to do.
        """
        for key in self.eligible_controllers:
            if len(self.eligible_controllers[key]) < 2:
                print("Not enough controllers for unit: ", key)
                return
        print("Data Valid")
        return
        # (To be Done) Validate given data here with more constraints.

    def set_eligible_controllers(self, controllers):
        """ 
            This function sets the global dict of eligible controllers as value, mapped to each unit as key at the beginning.
            This dict stays constant for reference.
        """

        eligible_controllers = {}
        for unit in self.units:
            filtered_controllers = [
                ctrl for ctrl in controllers if unit.name in ctrl.ratings]
            eligible_controllers[unit] = sorted(
                filtered_controllers, key=lambda x: x.currencies[unit.name], reverse=True)
        print(eligible_controllers)
        return eligible_controllers

    def get_next_unit(self):
        """
            Returns the unit with least number of available controllers at any given timeslot.
            This ensures units with lesser controllers are rostered first, to prevent an empty list
            for them later on if they are rostered at a lower rank.
        """

        available_controllers = self.get_available_controllers()
        free_units = dict(filter(
            lambda x: x[0].assign_next_at == self.time_slot, available_controllers.items()))
        # print(type(free_units))
        sorted_units = sorted(free_units,
                              key=lambda x: len(free_units[x]))
        # print("Sorted Units: ", sorted_units)
        return sorted_units[0]

    def get_available_controllers(self):
        """
            Returns a dict of available controllers taht are filtered and mapped by 2 sub functions.
            Available controlelrs takes eligible controllers and filters it for a given time slot and returns 
            a dict of controllers who are free to work and do not violate constraints of break time. 
        """

        def filter_fn(ctrl):
            """
                filter_fn filters the dictionary by a controller and checks if he is -
                1. Free - i.e he is not working/assigned anywhere else.
                2. His break time is over, i.e his last work time was at least one timeslot before the current timeslot in consideration.
            """
            if self.time_slot != 0:
                is_break_time_over = (
                    self.time_slot - ctrl.last_work_time) > self.required_break_time
            else:
                is_break_time_over = True

            is_free = not ctrl.is_working
            return is_free and is_break_time_over

        def map_fn(item):
            """
                Maps the filter_fn across the list of controllers for each unit.
            """
            ctrls = item[1]
            return (item[0], list(filter(filter_fn, ctrls)))

        available_controllers = dict(
            map(map_fn, self.eligible_controllers.items()))
        return available_controllers

    def get_next_controller(self, unit):
        """
            Returns the controller with most time remaining to work in a given list of controllers for a given unit.
            Sorts list of controller objects for given unit object based on controller's currency in descending order.
        """
        all_controllers_for_unit = self.get_available_controllers()[unit]

        def controller_sorted(ctrl):
            return ctrl.currencies[unit.name]

        sorted_by_currency = sorted(
            all_controllers_for_unit, key=controller_sorted, reverse=True)
        return sorted_by_currency[0]

    def create_roster(self):
        """
            Loops over shift_duration in blocks of break_time (0.5 in our case). 
            Fetch free units at given time slot, i.e - units which need to be assigned at given time slot.
            Loops over free units and sets and removes controllers, fixes assign_next_at for them based on controller's currency.
            Repeat till shift ends.
        """
        for time in np.arange(0, self.shift_duration, 0.5):

            free_units = dict(filter(
                lambda x: x[0].assign_next_at == self.time_slot, self.get_available_controllers().items()))

            for i in range(0, len(free_units)):
                next_unit = self.get_next_unit()
                ctrl = self.get_next_controller(next_unit)
                next_unit.set_assigned_controller(ctrl, time)
            self.roster[self.time_slot] = dict(
                [(unit.name, unit.assigned_controller.id) for unit in self.units])
            print("Roster for timeslot ", self.time_slot, "\n\n")
            print(json.dumps(self.roster[self.time_slot], indent=4), "\n\n")
            self.time_slot += 0.5
        return self.roster

    def print_roster(self):
        """
            Prints roster in time table format.
            Y-axis = Timeslots
            X-axis = Units
        """
        print("\nFINAL ROSTER FOR THE GIVEN SHIFT\n")
        for i in np.arange(0, self.shift_duration, 0.5):
            print(f"\t\t{i}", end="")
        for unit in self.units:
            print(f"\n{unit}\t", end="")
            for j in np.arange(0, self.shift_duration, 0.5):
                assigned_guy = self.roster[j][unit.name]
                print(f"\t{assigned_guy}", end="")
        print("\n")


class Unit:
    def __init__(self, name):
        self.name = name
        self.assign_next_at = 0
        self.assigned_controller = None

    def set_assigned_controller(self, new_controller, time):
        """
            Sets assigned controller based on conditions - 
            1. If no one is assigned in unit, assign.
            2. If unit already assigned, set is_working to False for existing controller,
            assign new controller, set is_working to True for him
            3. Set assign_next_at for controller (time duration to work, basically) based on currency value.
            4. Update currency for old controller
        """
        if self.assigned_controller == None:
            self.assigned_controller = new_controller
        else:
            old_controller = self.assigned_controller
            self.assigned_controller = new_controller
            old_controller.is_working = False
            old_controller.last_work_time = time
        new_controller.is_working = True
        self.set_next_assign_time(time)
        new_controller.update_currency(self.name, self.assign_next_at)

    def set_next_assign_time(self, time):
        """
            Sets assign_next_at based on if else conditions using currency value for given unit in consideration.
        """
        currency = self.assigned_controller.currencies[self.name]
        if currency >= 2:
            self.assign_next_at = time + 2
        elif currency < 2 and currency > 1:
            self.assign_next_at = time + 1.5
        elif currency > 0.5 and currency <= 1:
            self.assign_next_at = time + 1
        else:
            self.assign_next_at = time + 0.5

    def __str__(self):
        return self.name


class Controller:
    def __init__(self, id, rating_list):
        """
            id = controller id (ex. 10013995)
            ratings = list of ratings for controller
            currencies = dict of format unit: currency value (random int between 0 and 6)
            is_working = True if controller is currently assigned to a unit
            last_work_time = timeslot when the controller was replaced by another in the roster.
        """
        self.id = id
        self.ratings = self.set_ratings(rating_list)
        self.currencies = self.set_currency()
        self.is_working = False
        self.last_work_time = 0

    def set_last_work_time(self, time):
        self.last_work_time = time

    def set_ratings(self, rating_list):
        """
            Takes a list of ratings and assigns it to given controller.
        """
        ratings = {}
        for rating in rating_list:
            ratings[rating] = True
        return ratings

    def set_currency(self):
        """
            Sets currency for each rating as a random integer between 0 and 6.
        """
        currencies = {}
        for rating in self.ratings:
            random.seed()
            currencies[rating] = random.randint(0, 6)
        return currencies

    def update_currency(self, rating, time_worked):
        """
            Subtracts time_worked from currency.
        """
        self.currencies[rating] -= time_worked

    def __str__(self):
        return self.id


# Data Creation

# Create Unit objects
U1 = Unit('UMMP')
U2 = Unit('UMMR')
U3 = Unit('UHSP')
U4 = Unit('UHSR')
U5 = Unit('ADSC')
U6 = Unit('OCE')
U7 = Unit('WSO')

unit_list = [U1, U2, U3, U4, U5, U6, U7]

ratings = [u.name for u in unit_list]

# Assigns ID, and random sample of rating list to each conroller.
C1 = Controller('10013968', random.sample(
    ratings, random.randint(1, len(ratings))))
C2 = Controller('10013969', random.sample(
    ratings, random.randint(1, len(ratings))))
C3 = Controller('10013960', random.sample(
    ratings, random.randint(1, len(ratings))))
C4 = Controller('10013961', random.sample(
    ratings, random.randint(1, len(ratings))))
C5 = Controller('10013962', random.sample(
    ratings, random.randint(1, len(ratings))))
C6 = Controller('10013963', random.sample(
    ratings, random.randint(1, len(ratings))))
C7 = Controller('10013964', random.sample(
    ratings, random.randint(1, len(ratings))))
C8 = Controller('10013965', random.sample(
    ratings, random.randint(1, len(ratings))))
C9 = Controller('10013966', random.sample(
    ratings, random.randint(1, len(ratings))))
C10 = Controller('10013967', random.sample(
    ratings, random.randint(1, len(ratings))))
C11 = Controller('10013970', random.sample(
    ratings, random.randint(1, len(ratings))))
C12 = Controller('10013971', random.sample(
    ratings, random.randint(1, len(ratings))))
C13 = Controller('10013972', random.sample(
    ratings, random.randint(1, len(ratings))))
C14 = Controller('10013973', random.sample(
    ratings, random.randint(1, len(ratings))))
C15 = Controller('10013974', random.sample(
    ratings, random.randint(1, len(ratings))))
C16 = Controller('10013958', random.sample(
    ratings, random.randint(1, len(ratings))))
C17 = Controller('10013948', random.sample(
    ratings, random.randint(1, len(ratings))))
C18 = Controller('10013938', random.sample(
    ratings, random.randint(1, len(ratings))))
C19 = Controller('10013928', random.sample(
    ratings, random.randint(1, len(ratings))))
C20 = Controller('10013918', random.sample(
    ratings, random.randint(1, len(ratings))))

controllers = [C1, C2, C3, C4, C5, C6, C7, C8, C9, C10,
               C11, C12, C13, C14, C15, C16, C17, C18, C19, C20]

data = {}
ctrl_dict = {}
for controller in controllers:
    ctrl_dict[controller.id] = controller.currencies

data['units'] = ratings
data['controllers'] = ctrl_dict

# Save data in file
with open('data.txt', 'w') as outfile:
    json.dump(data, outfile, indent=4)

# Create roster

roster = Roster(unit_list, controllers, 6)
final_roster = roster.create_roster()
roster.print_roster()

# Save roster in file
with open('roster.txt', 'w') as outfile:
    json.dump(final_roster, outfile, indent=4)
