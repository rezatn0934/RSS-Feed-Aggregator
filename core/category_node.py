from abc import ABC, abstractmethod


class Node(ABC):
    children = []

    @abstractmethod
    def __init__(self, parent=None):
        assert parent is None or isinstance(parent, Node)
        self.children = []
        self.parent = parent

        if parent:
            self.parent.children.append(self)

    def print_tree(self, prefix='', last=False):
        pointer = '\u2514' if last else ('\u251C' if prefix else '')
        print(prefix + pointer, repr(self))

        for i, child in enumerate(self.children):
            last = i == len(self.children) - 1
            if last:
                child.print_tree(prefix + '\t ', last=True)
            else:
                child.print_tree(prefix + '\t|')

    def remove(self):
        if self.parent:
            self.parent.children.remove(self)

    def walk_children(self):
        yield (self, self.children)


class Category(Node):
    def __init__(self, name, parent=None):
        super().__init__(parent)
        self.name = name

    def __repr__(self):
        return self.name
