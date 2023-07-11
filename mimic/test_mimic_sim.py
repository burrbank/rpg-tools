import random
from mimic_sim import Direction, Room, Node, Map, load_map_yaml

SIMPLE_MAP = """  A C
  | |
B-+-+-D
  |
  E"""


def test_render():

    room_a = Room("A")
    node_1 = Node("1")
    node_1.set_connection(room_a, Direction.NORTH)
    room_b = Room("B")
    room_b.set_connection(node_1, Direction.EAST)
    room_e = Room("E")
    room_e.set_connection(node_1, Direction.NORTH)
    node_2 = Node("2")
    node_2.set_connection(node_1, Direction.WEST)
    room_c = Room("C")
    room_c.set_connection(node_2, Direction.SOUTH)
    room_d = Room("D")
    room_d.set_connection(node_2, Direction.WEST)

    results = []
    for _ in range(5):
        ship_map = Map()
        ship_map.insert_room(random.choice([room_a, room_b, room_c, room_d, room_e]), (0, 0))
        res = ship_map.render()
        print(res)
        results.append(res)
    print(SIMPLE_MAP)

    assert all([x == SIMPLE_MAP for x in results])


def test_load():
    ship_map, _ = load_map_yaml("simple_map.yml")

    res = ship_map.render()
    assert res == SIMPLE_MAP

def test_replace():
    ship_map, _ = load_map_yaml("simple_map.yml")

    a_pos = ship_map.coord_lookup["A"]

    room_f = Room("F")

    ship_map.insert_room(room_f, a_pos)

    assert room_f.south == "1"
    assert ship_map.room_lookup["1"].north == "F"
