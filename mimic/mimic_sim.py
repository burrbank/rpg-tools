from __future__ import annotations
import time
from colorama import Fore
from enum import Enum
from functools import cached_property
import random
from typing import Dict, List, Tuple

import yaml

LIGHTUP_SEQUENCE = [Fore.CYAN, Fore.MAGENTA, Fore.YELLOW, Fore.GREEN, Fore.RED]


class Map:
    def __init__(self) -> None:
        self._data = {}
        self.rendered = set()

    def insert_value(self, coord: Tuple[int, int], value: str | Room | Node):
        assert len(coord) == 2

        content = self._data.get(coord)
        if not content or not isinstance(content, (Room, Node)):
            self._data[coord] = value
            return

        content.replace(value)
        self._data[coord] = value

    def reset_render(self):
        self.rendered = set()

    def render(self):
        min_x = 0
        min_y = 0
        max_x = 0
        max_y = 0

        for x, y in self._data.keys():
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
                char = self._data.get((x, y), " ")
                if isinstance(char, (Node, Room)):
                    char = char.render()
                line.append(char)

            final.append("".join(line))

        return "\n".join((x.rstrip() for x in final))

    def insert_room(self, room: Room | Node, coord: Tuple[int, int]):
        if room in self.rendered:
            return
        self.insert_value(coord, room)
        self.rendered.add(room)

        for direction in Direction:
            self.insert_connected(room, direction, coord)

    def insert_connected(self, room, direction, coord):
        if not getattr(room, direction.value):
            return
        delta = Delta.from_direction(direction)
        temp = add_coords(coord, delta.value)
        if direction in (Direction.NORTH, Direction.SOUTH):
            self.insert_value(temp, "|")
        else:
            self.insert_value(temp, "-")

        temp = add_coords(temp, delta.value)

        self.insert_room(getattr(room, direction.value), temp)

    @property
    def rooms(self):
        return [x for x in self._data.values() if isinstance(x, (Node, Room))]

    @property
    def room_lookup(self):
        return {x.name: x for x in self._data.values() if isinstance(x, (Node, Room))}

    @property
    def coord_lookup(self):
        return {
            y.name: x for x, y in self._data.items() if isinstance(y, (Node, Room))
        }

    @property
    def rendered_rooms(self):
        return len(
            self.rooms
        )

    @property
    def existant_rooms(self):
        rooms = set()
        for room in self.rooms:
            rooms.add(room.name)
            for direction in Direction:
                connected = getattr(room, direction.value)
                if connected:
                    rooms.add

        return len(rooms)

def add_coords(coord_1, coord_2):
    return tuple(sum(x) for x in zip(coord_1, coord_2))

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
                    for x in ["name",]
                )
            )
        return False

    def render(self) -> str:
        if self.color:
            return self.color + self.name[0] + Fore.RESET
        return self.name[0]

    def replace(self, other):
        for direction in Direction:

            connection = getattr(self, direction.value)
            if connection:
                setattr(connection, Direction.opposite(direction).value, other)
                setattr(other, direction.value, connection)

class Node(Room):
    def render(self) -> str:
        if self.color:
            return self.color + "+" + Fore.RESET
        return "+"


def split(data: list, chunk_size):
    for i in range(0, len(data), chunk_size):
        yield data[i : i + chunk_size]


def load_map_yaml(yaml_file):
    with open(yaml_file) as y_file:
        data = yaml.safe_load(y_file)

    ship_map = Map()

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

    ship_map.insert_room(created[0], (0, 0))

    return ship_map, data.get("room_table", [])


def does_it_panic(stress):
    roll = random.randint(1, 20)
    if roll > stress:
        return False
    return True


def panic_roll(
    room: Room,
    direction: Direction,
    ship_map: Map,
    stress: int,
    panic_room_table: List[str],
    created: Dict,
):
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
            if str(i) not in ship_map.room_lookup:
                break
            i += 1
        new_room = Node(str(i))

    else:
        new_room = panic_room_table[min(roll, len(panic_room_table) - 1)]

        i = 1
        while True:
            i += 1
            if new_room in ship_map.room_lookup:
                new_room = f"{new_room}_{i}"
            else:
                break

        new_room = Room(new_room)


    if room.name not in ship_map.room_lookup:
        print(f"Room not found {room.name} in map")
        return

    room.set_connection(new_room, direction)
    created.update({new_room.name: new_room})
    delta = add_coords(Delta.from_direction(direction).value, Delta.from_direction(direction).value)

    ship_map.insert_room(
        new_room, add_coords(ship_map.coord_lookup[room.name], delta)
    )

    for new_direction in Direction:
        if new_direction == Direction.opposite(direction):
            continue
        roll = random.randint(1, 3)
        if roll == 1:
            stress += 1
            panic_roll(
                new_room, new_direction, ship_map, stress, panic_room_table, created
            )

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


def handle_panic(room:str, direction:str, ship_map:Map, stress:int, panic_room_table:List[str]):
    room = ship_map.room_lookup.get(room, None)
    if room is None:
        print(f"Room '{room}' not found.")
        return stress
    created = {}
    stress = panic_roll(
        room, Direction(direction), ship_map, stress, panic_room_table, created
    )
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


def clear_colors(ship_map: Map):
    for x in ship_map.rooms:
        x.reset_color()


def handle_input(inp, ship_map: Map, stress: int, panic_room_table: List[str]):
    clear_colors(ship_map)
    match inp.split():
        case ["list"]:
            print(ship_map.rooms)
        case ["add", name, direction, other]:
            handle_adding_rooms(ship_map, name, direction, other)
        case ["panic", room, direction]:
            stress = handle_panic(room, direction, ship_map, stress, panic_room_table)
        case ["stress", cmd, value]:
            stress = handle_stress_commands(stress, cmd, value)
        case ["reload"]:
            ship_map, panic_room_table = load_map_yaml("hms_midgard.yml")
            stress = 0
        case ["highlight", *targets]:
            for x in targets:
                ship_map.room_lookup[x].color = Fore.YELLOW
        case ["lightup"]:
            execute_lightup(ship_map, stress)
        case ["walk", room]:
            execute_walk(room, ship_map, stress)
        case ["exit"]:
            exit()
        case _:
            print("Command not found")

    print("\n")
    return stress, panic_room_table


def execute_lightup(ship_map: Map, stress: int):
    for batch in split(ship_map.rooms, len(LIGHTUP_SEQUENCE)):
        string = ["["]

        for room, color in zip(batch, LIGHTUP_SEQUENCE):
            room.color = color
            string.append(color + f"{room.name}, ")

        string.append(Fore.RESET + "]")
        print("".join(string))

        print(ship_map.render())

        print(f"\nSTRESS: {stress}")


        for x in batch:
            x.reset_color()

        input("\n lightup next > ")


def execute_walk(room: str, ship_map: Map, stress: int):
    location = ship_map.room_lookup[room]
    while True:
        print("\n")
        location.color = Fore.YELLOW
        print(Fore.YELLOW + location.name + Fore.RESET)

        print(ship_map.render())

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
    ship_map, room_table = load_map_yaml("hms_midgard.yml")
    stress = 0
    while True:
        print(ship_map.render())

        print(f"\nSTRESS: {stress}")

        inp = input("\n> ")
        stress, room_table = handle_input(inp, ship_map, stress, room_table)


if __name__ == "__main__":
    main()
