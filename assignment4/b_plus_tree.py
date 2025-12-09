import math

class Node:
    def __init__(self, is_leaf=False):
        self.keys = []
        self.children = []
        self.is_leaf = is_leaf
        self.next = None
        self.parent = None

class BPlusTree:
    def __init__(self, degree=4):
        self.degree = degree
        # Minimum number of keys for non-root node
        self.min_keys = math.ceil(degree / 2) - 1
        self.root = Node(is_leaf=True)

    def search(self, key):

        node = self._find_leaf(key)
        for k in node.keys:
            if k == key:
                return True
        return False

    def _find_leaf(self, key):
        node = self.root
        while not node.is_leaf:
            i = 0
            while i < len(node.keys) and key >= node.keys[i]:
                i += 1
            node = node.children[i]
        return node

    def insert(self, key):

        if self.search(key):
            return False # Duplicate keys are not allowed

        leaf = self._find_leaf(key)
        
        # Insert into leaf
        self._insert_into_leaf(leaf, key)
        
        # Check for overflow
        if len(leaf.keys) == self.degree:
            self._split_leaf(leaf)
            
        return True

    def _insert_into_leaf(self, leaf, key):
        # Insert sorted
        index = 0
        while index < len(leaf.keys) and key > leaf.keys[index]:
            index += 1
        leaf.keys.insert(index, key)

    def _split_leaf(self, leaf):
        # Split leaf into two
        mid = len(leaf.keys) // 2
        
        new_leaf = Node(is_leaf=True)
        new_leaf.keys = leaf.keys[mid:]
        leaf.keys = leaf.keys[:mid]
        
        new_leaf.next = leaf.next
        leaf.next = new_leaf
        new_leaf.parent = leaf.parent
        
        # Propagate to parent
        self._insert_into_parent(leaf, new_leaf.keys[0], new_leaf)

    def _insert_into_parent(self, left, key, right):
        parent = left.parent
        
        if parent is None:
            # Create new root
            new_root = Node(is_leaf=False)
            new_root.keys = [key]
            new_root.children = [left, right]
            self.root = new_root
            left.parent = new_root
            right.parent = new_root
            return

        # Insert key into parent
        index = 0
        while index < len(parent.keys) and key > parent.keys[index]:
            index += 1
        parent.keys.insert(index, key)
        parent.children.insert(index + 1, right)
        right.parent = parent
        
        if len(parent.keys) == self.degree:
            self._split_internal(parent)

    def _split_internal(self, node):
        mid = len(node.keys) // 2
        up_key = node.keys[mid]
        
        new_node = Node(is_leaf=False)
        new_node.keys = node.keys[mid+1:]
        new_node.children = node.children[mid+1:]
        
        # Update parent pointers for children moved to new_node
        for child in new_node.children:
            child.parent = new_node
            
        node.keys = node.keys[:mid]
        node.children = node.children[:mid+1]
        new_node.parent = node.parent
        
        self._insert_into_parent(node, up_key, new_node)

    def delete(self, key):
        if not self.search(key):
            return False
            
        leaf = self._find_leaf(key)
        leaf.keys.remove(key)
        
        if leaf == self.root:
            # If root is leaf, no underflow handling needed unless we want to handle empty tree
            return True
            
        if len(leaf.keys) < self.min_keys:
            self._handle_underflow(leaf)
        return True

    def _handle_underflow(self, node):
        if node == self.root:
            if len(node.keys) == 0 and not node.is_leaf:
                self.root = node.children[0]
                self.root.parent = None
            return

        parent = node.parent
        # Find index of node in parent's children
        index = parent.children.index(node)
        
        # Try borrow from left sibling
        if index > 0:
            left_sibling = parent.children[index - 1]
            if len(left_sibling.keys) > self.min_keys:
                self._borrow_from_left(node, left_sibling, index - 1)
                return
        
        # Try borrow from right sibling
        if index < len(parent.children) - 1:
            right_sibling = parent.children[index + 1]
            if len(right_sibling.keys) > self.min_keys:
                self._borrow_from_right(node, right_sibling, index)
                return
                
        # Merge
        if index > 0:
            # Merge with left
            self._merge(parent.children[index - 1], node, index - 1)
        else:
            # Merge with right
            self._merge(node, parent.children[index + 1], index)

    def _borrow_from_left(self, node, sibling, parent_key_index):
        parent = node.parent
        
        if node.is_leaf:
            borrowed_key = sibling.keys.pop()
            node.keys.insert(0, borrowed_key)
            parent.keys[parent_key_index] = node.keys[0]
        else:
            borrowed_key = sibling.keys.pop()
            borrowed_child = sibling.children.pop()
            
            # Move parent key down
            node.keys.insert(0, parent.keys[parent_key_index])
            node.children.insert(0, borrowed_child)
            borrowed_child.parent = node
            
            # Move sibling key up
            parent.keys[parent_key_index] = borrowed_key

    def _borrow_from_right(self, node, sibling, parent_key_index):
        parent = node.parent
        
        if node.is_leaf:
            borrowed_key = sibling.keys.pop(0)
            node.keys.append(borrowed_key)
            parent.keys[parent_key_index] = sibling.keys[0]
        else:
            borrowed_key = sibling.keys.pop(0)
            borrowed_child = sibling.children.pop(0)
            
            # Move parent key down
            node.keys.append(parent.keys[parent_key_index])
            node.children.append(borrowed_child)
            borrowed_child.parent = node
            
            # Move sibling key up
            parent.keys[parent_key_index] = borrowed_key

    def _merge(self, left, right, parent_key_index):
        parent = left.parent
        
        if left.is_leaf:
            left.keys.extend(right.keys)
            left.next = right.next
            
            # Remove key from parent and right child
            parent.keys.pop(parent_key_index)
            parent.children.pop(parent_key_index + 1)
        else:
            # Internal node merge
            # Pull down parent key
            left.keys.append(parent.keys[parent_key_index])
            left.keys.extend(right.keys)
            left.children.extend(right.children)
            
            for child in right.children:
                child.parent = left
                
            parent.keys.pop(parent_key_index)
            parent.children.pop(parent_key_index + 1)
            
        if len(parent.keys) < self.min_keys:
            self._handle_underflow(parent)

    def display(self):

        node = self.root
        while not node.is_leaf:
            node = node.children[0]
        
        result = []
        while node:
            result.extend(node.keys)
            node = node.next
        print(",".join(map(str, result)))

if __name__ == "__main__":
    tree = BPlusTree(degree=4)

    print("Inserting 10, 20, 5, 15")
    tree.insert(10)
    tree.insert(20)
    tree.insert(5)
    tree.insert(15)

    print("Display after insert:")
    tree.display()  

    print(f"Search 15: {tree.search(15)}")  # True
    print(f"Search 100: {tree.search(100)}") # False

    print("Deleting 10")
    tree.delete(10)

    print("Display after delete:")
    tree.display()  # 输出：5,15,20
