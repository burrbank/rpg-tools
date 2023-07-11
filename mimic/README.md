# mimic sim

Interactive tool for running and testing procedures for Mimic (a Mothership adventure I'm working on)

# setup
this was written using `python3.10.6` and requires a version of python that has the match/case feature (at least 3.10).

```
pip install -r requirements.txt

python mimic_sim.py
```
Currently it needs to be run from the same directory as `hms_midgard.yml`.

# Commands

## list
`list`
will list out all current rooms.

## add
`list (room name) (north|east|south|west) (new room name)`
will create a new room to in the direction given.

## panic
`panic (room name) (direction)`
Makes random room rolls based on current stress. Will create the first room in the direction given, from the room given.

## stress
`stress (add|sub) (integer)`
Add or subtract from the current stress.

## reload
`reload`
re-initialize the ship as discribed in `hms_misgard.yml`

## highlight
`highlight target_1 target_2 ...`
will display listed target rooms as yellow on the map.

## lightup
`lightup`
will iterate through all rooms (5 at a time) with different colors.

## walk
`walk (starting room)`
will enter into a walk mode, will print current room in yellow, move around using north|east|south|west.

## exit
`exit`
will terminate the program.