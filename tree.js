/*

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

*/

const { produce } = require("immer");
const { scaleTime, domain, timeMinute, range } = require("d3");

const CONTROLLER_NAMES = Array.from({ length: 20 }, (_, i) =>
  String.fromCharCode(65 + i)
);

const UNIT_NAMES = Array.from(
  { length: 10 },
  (_, i) => "U" + String.fromCharCode(65 + i)
);

const TIME_SCALE = scaleTime().domain([
  new Date(2021, 0, 1, 0),
  new Date(2021, 0, 1, 4),
]);

const TIME_SLOTS = TIME_SCALE.ticks(timeMinute.every(30));

const DEPTH = UNIT_NAMES.length * TIME_SLOTS.length;

let controllers = {};
let units = {};

const getRandomRatings = () => {
  let ratings = {};
  UNIT_NAMES.map((unit) => {
    const seed = Math.random();
    if (seed > 0.5) {
      ratings[unit] = false;
    } else {
      ratings[unit] = true;
    }
  });
  return ratings;
};

CONTROLLER_NAMES.map((controllerName) => {
  let ratings = getRandomRatings();
  controllers[controllerName] = {
    workingOn: null,
    workedFor: null,
    currency: Math.floor(Math.random * 100),
    inQueue: true,
    ratings: ratings,
  };
});

UNIT_NAMES.map((unitName) => {
  units[unitName] = {
    assignedTo: null,
    history: null,
  };
});

const fetchAvailableControllers = (unitName) => {
  let availableControllers = {};
  Object.keys(controllers).map((controllerName) => {
    if (
      controllers[controllerName].ratings[unitName] &&
      controllers[controllerName].workingOn !== unitName &&
      controllers[controllerName].inQueue === true
    ) {
      availableControllers[controllerName] = controllers[controllerName];
    }
  });
  return availableControllers;
};

const relieve = (controllerName, backtrack = false) => {
  if (controllerName === null) {
    console.log("NO ONE TO SIGN OFF!");
    return;
  }
  currentUnitName = controllers[controllerName].workingOn;
  units[currentUnitName].history = controllerName;
  units[currentUnitName].assignedTo = null;
  controllers[controllerName].currency -= 30;
  controllers[controllerName].workedFor += 30;
  controllers[controllerName].workingOn = null;
  controllers[controllerName].inQueue = false || backtrack;
  console.log(`SIGNED OFF ${controllerName} from ${currentUnitName}!`);
  console.log(
    `Relieved Queue status of ${controllerName}`,
    controllers[controllerName].inQueue
  );
};

const assign = (controllerName, unitName, backtrack = false) => {
  if (controllerName.workingOn) {
    currentUnitName = controllers[controllerName].workingOn;
  }
  controllers[controllerName].workingOn = unitName;
  units[unitName].assignedTo = controllerName;
  controllers[controllerName].inQueue = false || backtrack;
  console.log(
    `SIGNED IN ${controllerName} to ${controllers[controllerName].workingOn}!`
  );
  console.log(
    `Assigned Queue status of ${controllerName}`,
    controllers[controllerName].inQueue
  );
};

const initial = {};

UNIT_NAMES.map((unitName) => {
  const available = Object.keys(fetchAvailableControllers(unitName));
  initial[unitName] = available;
});

console.log("INITIAL STATE:");
console.log(initial);
console.log("\n");

const wakeup = () => {
  Object.keys(controllers).map((controllerName) => {
    if (
      controllers[controllerName].workingOn === null &&
      controllers[controllerName].inQueue === false
    ) {
      controllers[controllerName].inQueue = true;
    }
  });
};

TIME_SLOTS.slice(0, 3).map((slot, number) => {
  console.log(`TIMESLOT #${number + 1} at ${slot.toString().slice(0, 25)}`);

  wakeup();
  let available = {};

  CONTROLLER_NAMES.map((controllerName) => {
    available[controllerName] = false;
  });

  let roster = {};
  for (let i = 0; i < UNIT_NAMES.length; i++) {
    console.log(i);
    const unitName = UNIT_NAMES[i];
    console.log(`POLLING FOR ${unitName}!`);
    console.log(`CONTROLLERS AVAILABLE:`);

    let newAvailable = {};
    Object.keys(fetchAvailableControllers(unitName)).map((controllerName) => {
      newAvailable[controllerName] = false || available[controllerName];
    });
    available = newAvailable;

    console.log(available);

    let success = false;

    while (!success) {
      try {
        let chosenControllerName;
        chosenControllerName = Object.keys(available).find(
          (availableKey) => available[availableKey] === false
        );
        available[chosenControllerName] = true;
        console.log(`CONTROLLER CHOSEN: ${chosenControllerName}`);
        const previousControllerName = units[unitName].assignedTo;
        relieve(previousControllerName);
        assign(chosenControllerName, unitName);
        roster[unitName] = chosenControllerName;
        success = true;
        available = {};
      } catch (error) {
        console.log("ERROR!");
        --i;
        history_guy = units[UNIT_NAMES[i]].history;
        console.log("History guy", history_guy);
        relieve(units[UNIT_NAMES[i]].assignedTo, true);
        assign(history_guy, UNIT_NAMES[i], true);
        --i;
        console.log(i);
        break;
      }
    }

    console.log("\n------------\n");
  }

  console.log("ROSTER: ");
  console.log(roster);
});
