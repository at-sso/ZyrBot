from typing import Optional, Union


# Unified Linear Data Structure for Stack and Queue
class LinearDataStructure:
    def __init__(self, mode: str = "stack") -> None:
        self.items: list[Union[str, float]] = []
        self.mode: str = mode  # "stack" for LIFO, "queue" for FIFO

    def is_empty(self) -> bool:
        return len(self.items) == 0

    def add(self, item: Union[str, float]) -> None:
        self.items.append(item)

    def remove(self) -> Union[str, float]:
        if not self.is_empty():
            return self.items.pop() if self.mode == "stack" else self.items.pop(0)
        raise IndexError("Remove from an empty data structure")

    def peek(self) -> Union[str, float]:
        if not self.is_empty():
            return self.items[-1] if self.mode == "stack" else self.items[0]
        raise IndexError("Peek from an empty data structure")


# Linked List Implementation
class _Node:
    def __init__(self, data: float) -> None:
        self.data: float = data
        self.next: Optional[_Node] = None


class LinkedList:
    def __init__(self) -> None:
        self.head: Optional[_Node] = None

    def append(self, data: float) -> None:
        new_node = _Node(data)
        if not self.head:
            self.head = new_node
            return
        last = self.head
        while last.next:
            last = last.next
        last.next = new_node

    def remove(self, key: float) -> None:
        current = self.head
        if current and current.data == key:
            self.head = current.next
            return
        prev = None
        while current and current.data != key:
            prev = current
            current = current.next
        if current:
            prev.next = current.next

    def search(self, key: float) -> bool:
        current = self.head
        while current:
            if current.data == key:
                return True
            current = current.next
        return False
