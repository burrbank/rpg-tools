import random
from mimic_sim import *

SIMPLE_MAP = '''  A C
  | |
B-+-+-D
  |
  E'''


def test_render():
    room_a = Room('A')
    node_1 = Node('1')
    node_1.set_connection(room_a, Direction.NORTH)
    room_b = Room('B')
    room_b.set_connection(node_1, Direction.EAST)
    room_e = Room('E')
    room_e.set_connection(node_1, Direction.NORTH)
    node_2 = Node('2')
    node_2.set_connection(node_1, Direction.WEST)
    room_c = Room('C')
    room_c.set_connection(node_2, Direction.SOUTH)
    room_d = Room("D")
    room_d.set_connection(node_2, Direction.WEST)

    results = []
    for _ in range(5):
        res = render_connected(
            random.choice(
                [room_a, room_b, room_c, room_d, room_e, node_1, node_2]
            )
        )
        print(res)
        results.append(res)
    print(SIMPLE_MAP)

    assert all([x == SIMPLE_MAP for x in results])


def test_load():
    rooms = load_map_yaml("simple_map.yml")

    res = render_connected(
        random.choice(
            list(rooms.values())
        )
    )
    assert res == SIMPLE_MAP
