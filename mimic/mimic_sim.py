from __future__ import annotations
from colorama import Fore
from enum import Enum
from itertools import count
import random
from typing import Dict, List, Tuple
import sys

import yaml

LIGHTUP_SEQUENCE = [
    Fore.CYAN, Fore.MAGENTA, Fore.YELLOW, Fore.GREEN, Fore.RED
]

class Map:
    def __init__(self) -> None:
        self.data = {}
        self.rendered = set()

    def insert_value(self, coord: Tuple[int, int], value: str):
        assert len(coord) == 2
        self.data[coord] = value

    def reset_render(self):
        self.rendered = set()

    def render(self):
        min_x = 0
        min_y = 0
        max_x = 0
        max_y = 0

        for x, y in self.data.keys():
            if min_x > x:
                min_x = x
            if max_x < x:
                max_x = x
            if min_y > y:
                min_y = y
            if max_y < y:
                max_y = y
        final = []

        for y in range(min_y, max_y + 1):
            line = []
            for x in range(min_x, max_x + 1):
                line.append(self.data.get((x, y), " "))
            final.append("".join(line))

        return "\n".join((x.rstrip() for x in final))


class Direction(Enum):
    NORTH = "north"
    EAST = "east"
    SOUTH = "south"
    WEST = "west"

    @staticmethod
    def opposite(direction: Direction):
        match direction:
            case Direction.NORTH:
                return Direction.SOUTH
            case Direction.EAST:
                return Direction.WEST
            case Direction.SOUTH:
                return Direction.NORTH
            case Direction.WEST:
                return Direction.EAST


class Delta(Enum):
    NORTH = (0, -1)
    EAST = (1, 0)
    SOUTH = (0, 1)
    WEST = (-1, 0)

    @staticmethod
    def from_direction(direction):
        match direction:
            case Direction.NORTH:
                return Delta.NORTH
            case Direction.EAST:
                return Delta.EAST
            case Direction.SOUTH:
                return Delta.SOUTH
            case Direction.WEST:
                return Delta.WEST

class Room:
    def __init__(self, name: str) -> None:
        self.name = name

        self.north = None
        self.east = None
        self.south = None
        self.west = None
        self.color = None

    def set_connection(self, other, direction: Direction):
        setattr(self, direction.value, other)
        setattr(other, Direction.opposite(direction).value, self)

    def reset_color(self):
        self.color = None

    def __repr__(self) -> str:
        return self.name

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, str):
            return self.name == __value
        elif isinstance(__value, Room):
            return all(
                (
                    getattr(self, x) == getattr(self, x)
                    for x in ("name", "north", "east", "south", "west")
                )
            )
        return False

    def render(self) -> str:
        if self.color:
            return self.color + self.name[0] + Fore.RESET
        return self.name[0]


class Node(Room):
    def render(self) -> str:
        if self.color:
            return self.color + "+" + Fore.RESET
        return "+"


def render_connected(room: Room | Node):
    m = Map()
    current_pos = (0, 0)
    render_room(m, room, current_pos)

    return m.render()

def split(data:list, chunk_size):
    for i in range(0, len(data), chunk_size):
        yield data[i:i + chunk_size]

def render_room(m: Map, room: Room | Node, coord: Tuple[int, int]):
    if room in m.rendered:
        return
    m.insert_value(coord, room.render())
    m.rendered.add(room)

    for direction in Direction:
        render_direction(m, room, direction, coord)


def render_direction(map, room, direction, coord):
    if not getattr(room, direction.value):
        return
    delta = Delta.from_direction(direction)
    temp = tuple(sum(x) for x in zip(coord, delta.value))
    if direction in (Direction.NORTH, Direction.SOUTH):
        map.insert_value(temp, "|")
    else:
        map.insert_value(temp, "-")
    temp = tuple(sum(x) for x in zip(temp, delta.value))

    render_room(map, getattr(room, direction.value), temp)


def load_map_yaml(yaml_file):
    with open(yaml_file) as y_file:
        data = yaml.safe_load(y_file)

    created = []
    for name in data["rooms"]:
        created.append(Room(name))
    for i in range(data["nodes"]):
        created.append(Node(str(i + 1)))

    lookup: Dict[str, Room | Node] = {x.name: x for x in created}

    for connection in data["connections"]:
        room1, direction, room2 = connection.split(".")
        direction = Direction(direction)

        lookup[room1].set_connection(lookup[room2], direction)
    return lookup, data.get("room_table", [])


def does_it_panic(stress):
    roll = random.randint(1, 20)
    if roll > stress:
        return False
    return True


def panic_roll(room:Room, direction:Direction, rooms:Dict[str, Room], stress: int, panic_room_table:List[str], created:Dict):
    if not does_it_panic(stress):
        print("no panic, yet...")
        return stress + 1

    rolls = []
    for _ in range(stress // 10 + 1):
        rolls.append(random.randint(0, 9))
    roll = max(rolls)

    if roll == 9:
        roll = random.randint(0, 9) + 9

    if is_node(roll):
        i = 0
        while True:
            if not str(i) in rooms:
                break
            i += 1
        new_room = Node(str(i))

    else:
        new_room = panic_room_table[min(roll, len(panic_room_table) - 1)]

        i = 1
        while True:
            i += 1
            if new_room in rooms:
                print(f"Proposing new room {new_room}\r")
                new_room = f"{new_room}_{i}"
            else:
                break

        new_room = Room(new_room)

    room.set_connection(new_room, direction)
    created.update({new_room.name: new_room})
    rooms.update({new_room.name: new_room})
    for new_direction in Direction:
        if new_direction == Direction.opposite(direction):
            continue
        roll = random.randint(1, 3)
        if roll == 1:
            stress += 1
            panic_roll(new_room, new_direction, rooms, stress, panic_room_table, created)

    return stress

def is_node(roll):
    if roll == 8:
        is_node = True
    else:
        is_node = False
    return is_node


def handle_adding_rooms(rooms, name, direction, other):
    rooms[name] = Room(name)
    direction = Direction(direction)
    rooms[name].set_connection(rooms[other], Direction.opposite(direction))


def handle_panic(room, direction, rooms, stress, panic_room_table):
    room = rooms.get(room, None)
    if room is None:
        print(f"Room '{room}' not found.")
        return stress
    created = {}
    stress = panic_roll(room, Direction(direction), rooms, stress, panic_room_table, created)
    print(f"Created rooms: {list(created.keys())}")
    for x in created:
        created[x].color = Fore.GREEN
    return stress


def handle_stress_commands(stress, cmd, value):
    if cmd == "add":
        stress += int(value)
    elif cmd == "sub":
        stress -= int(value)
    else:
        print("Unknown stress command.")
    return stress

def clear_colors(rooms:Dict[str, Room|Node]):
    for x in rooms:
        rooms[x].reset_color()

def handle_input(inp, rooms: Dict[str, Room], stress, panic_room_table):
    clear_colors(rooms)
    match inp.split():
        case ["list"]:
            print(list(rooms.keys()))
        case ["add", name, direction, other]:
            handle_adding_rooms(rooms, name, direction, other)
        case ["panic", room, direction]:
            stress = handle_panic(room, direction, rooms, stress, panic_room_table)
        case ["stress", cmd, value]:
            stress = handle_stress_commands(stress, cmd, value)
        case ["reload"]:
            rooms, panic_room_table = load_map_yaml("hms_midgard.yml")
            stress = 0
        case ["highlight", *targets]:
            for x in targets:
                rooms[x].color = Fore.YELLOW
        case ["lightup"]:
            execute_lightup(rooms, stress)
        case ["walk", room]:
            execute_walk(rooms[room], stress)
        case ["exit"]:
            exit()
        case _:
            print("Command not found")

    print("\n")
    return rooms, stress, panic_room_table

def execute_lightup(rooms, stress):
    for batch in split(list(rooms.values()), len(LIGHTUP_SEQUENCE)):
        string = ["["]

        for room, color in zip(batch, LIGHTUP_SEQUENCE):
            room.color = color
            string.append(color + f"{room.name}, ")

        string.append(Fore.RESET + ']')
        print(''.join(string))

        print(render_connected(batch[0]))

        print(f"\nSTRESS: {stress}")

        for x in batch:
            x.reset_color()
        inp = input("\n lightup next > ")

def execute_walk(room, stress):
    location = room
    while True:
        print('\n')
        location.color = Fore.YELLOW
        print(Fore.YELLOW + location.name + Fore.RESET)

        print(render_connected(location))

        location.reset_color()

        print(f"\nSTRESS: {stress}")

        inp = input("walk > ")

        match inp:
            case Direction.NORTH.value:
                new = getattr(location, Direction.NORTH.value)
                location = new if new else location
            case Direction.EAST.value:
                new = getattr(location, Direction.EAST.value)
                location = new if new else location
            case Direction.SOUTH.value:
                new = getattr(location, Direction.SOUTH.value)
                location = new if new else location
            case Direction.WEST.value:
                new = getattr(location, Direction.WEST.value)
                location = new if new else location
            case _:
                return




def main():
    rooms, room_table = load_map_yaml("hms_midgard.yml")
    stress = 0
    while True:
        print(render_connected(rooms[random.sample(list(rooms.keys()), 1)[0]]))

        print(f"\nSTRESS: {stress}")

        inp = input("\n> ")
        rooms, stress, room_table = handle_input(inp, rooms, stress, room_table)


if __name__ == "__main__":
    main()
