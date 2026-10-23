"""Reference solution — human-written, used ONLY to validate the oracle tests."""


class Node:
    def __init__(self, val, next=None):
        self.val = val
        self.next = next


def has_cycle(head) -> bool:
    slow = fast = head
    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            return True
    return False
