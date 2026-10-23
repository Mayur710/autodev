from solution import Node, has_cycle


def build_list(values):
    """Build an acyclic linked list; return (head, tail)."""
    if not values:
        return None, None
    nodes = [Node(v) for v in values]
    for a, b in zip(nodes, nodes[1:]):
        a.next = b
    return nodes[0], nodes[-1]


def test_empty_list():
    assert has_cycle(None) is False


def test_single_node_no_cycle():
    head, _ = build_list([1])
    assert has_cycle(head) is False


def test_single_node_self_loop():
    n = Node(1)
    n.next = n
    assert has_cycle(n) is True


def test_cycle_in_middle():
    head, tail = build_list([1, 2, 3, 4])
    tail.next = head.next      # 4 -> 2
    assert has_cycle(head) is True


def test_cycle_at_tail_self_loop():
    head, tail = build_list([1, 2, 3])
    tail.next = tail
    assert has_cycle(head) is True


def test_cycle_back_to_head():
    head, tail = build_list([1, 2, 3])
    tail.next = head
    assert has_cycle(head) is True


def test_long_acyclic_list():
    head, _ = build_list(list(range(10_000)))
    assert has_cycle(head) is False
