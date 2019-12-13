from itertools import permutations
from copy import deepcopy


class Node:
    """Represents a binary tree visualization of a bracket."""

    def __init__(self, value, left=None, right=None, parent=None):
        """Create a node with left child left, right child right,
        and parent parent."""
        self.left = left
        self.right = right
        self.value = value
        self.parent = parent
        self.completed = False #True if the leaves in this subtree have been filled
        self.tokens = set() #empty until create_tokens called
        
        #if children assigned, make sure their parent pointers are accurate
        if left!=None:
            left.parent = self
        if right!=None:
            right.parent = self

    def is_leaf(self):
        """Returns true if this node has no children."""
        return self.left == None and self.right == None

    def sibling(self):
        """Returns the other child of this node's parent,
        if it exists.  Otherwise, return None."""
        if self.parent == None: return None
        if self.parent.left == self: return self.parent.right
        else:  return self.parent.left

    def find_largest_leaf(self):
        """Finds the largest leaf
        in the subtree starting at root."""
        if self.is_leaf():
            return self
        else:
            left_top = self.left.find_largest_leaf()
            right_top = self.right.find_largest_leaf()
            return max([left_top,right_top], key = lambda x: x.value)

    def find_rightmost_leaf(self):
        """Finds the rightmost leaf in a subtree starting at node."""
        if self.is_leaf(): return self
        else:  return self.right.find_rightmost_leaf()

    def find_leftmost_leaf(self):
        """Finds the leftmost node in a subtree starting at node."""
        if self.is_leaf(): return self
        else: return self.left.find_leftmost_leaf()

    def create_tokens(self):
        """Create tokens for this node and all inner nodes in subtree.
        Every node receives a token for every inner node in the subtree,
        and the tokens take on the values of those inner nodes."""
        if self.is_leaf(): return
        else:
            self.tokens = self.get_inner_node_values()
            self.left.create_tokens()
            self.right.create_tokens()

    def get_inner_node_values(self):
        """Returns a set of the values of the inner nodes in this subtree."""
        if self.is_leaf(): return set()
        else:
            values = self.right.get_inner_node_values()
            values.update(self.left.get_inner_node_values())
            values.add(self.value)
            return values

    def place_leaf_value(self, leaf_value, permutation):
        """Plays the 'token game' with leaf_value,
        where permutation is a list that dictates
        the priority of the tokens.

        If the leftmost leaf is available, it must
        receive the leaf_value, no tokens needed.

        If only rightmost leaf is available, it must
        receive the leaf_value, no tokens needed.

        Otherwise, whichever child has a token with
        greatest priority will use up that token
        and place the leaf_value in their subtree."""

        #places in leftmost leaf if available
        leftmost_leaf = self.find_leftmost_leaf()
        if leftmost_leaf.value == None:
            leftmost_leaf.value = leaf_value
            return

        #places in rightmost leaf if only availability
        if self.is_complete_except_rightmost():
            rightmost_leaf = self.find_rightmost_leaf()
            rightmost_leaf.value = leaf_value
            return

        #if either child is out of tokens, give to other child
        if len(self.left.tokens)==0:
            self.right.place_leaf_value(leaf_value, permutation)
            return
        elif len(self.right.tokens)==0:
            self.left.place_leaf_value(leaf_value, permutation)
            return

        #finds highest priority tokens of left and right children
        left_token = min(self.left.tokens, key = lambda x: permutation.index(x))
        right_token = min(self.right.tokens, key = lambda x: permutation.index(x))

        #passes leaf_value to child with highest priority token
        if permutation.index(left_token)<permutation.index(right_token):
            self.left.tokens.remove(left_token)
            self.left.place_leaf_value(leaf_value, permutation)
        else:
            self.right.tokens.remove(right_token)
            self.right.place_leaf_value(leaf_value, permutation)

    def is_complete_except_rightmost(self):
        """Returns true if all leaves have values
        except for the rightmost leaf."""
        if self.is_leaf(): #only rightmost gets here
            return self.value==None
        else:
            return (self.left.is_complete() and 
                    self.right.is_complete_except_rightmost())

    def is_complete(self):
        """Returns True if all leaves have values."""
        if self.is_leaf():
            return self.value!=None
        else:
            return self.left.is_complete and self.right.is_complete()

    def __str__(self):
        return tree_to_bracket(self).__str__()

######################

def construct_tree_framework(bracket):
    """Given the tree in bracket form, creates a tree with labeled leaves
    and unlabeled inner nodes."""
    if type(bracket)==int: #base case, creates leaf
        return Node(tree)

    else: #recursive step, inner nodes
        root = Node(None, construct_tree_framework(bracket[0]), construct_tree_framework(bracket[1]))
        return root

def fill_nodes(root):
    """Given a tree with labeled leaves and unlabeled inner nodes,
    gives a value to every non-leaf node, in standard traversal order.
    Mutates root, so does not return."""
    queue = [root]
    i = 1
    while queue != []:
        node = queue[-1]
        if node.left.value == None: #left child not visited
            queue.append(node.left)
        else:  #dequeue node and give value
            node.value = i 
            i += 1
            queue.pop()
            if not node.right.is_leaf(): #add right node to queue
                queue.append(node.right)

def bracket_to_tree(bracket):
    """Given a bracket, constructs and returns a tree representation using Nodes."""
    tree = construct_tree_framework(bracket)
    fill_nodes(tree)
    return tree

def tree_to_bracket(tree):
    """Given a tree as a Node, returns the bracket representation."""
    if tree.is_leaf():
        return tree.value
    
    else:
        return (tree_to_bracket(tree.left), tree_to_bracket(tree.right))


def perm_to_tree_structure(p):
    """Given a permutation p,
    creates the tree structure with non-leaf nodes labelled,
    and leaves have value None.
    Helper function."""
    perm = list(p)
    n = len(perm)+1
    root = Node(perm.pop(0))
    root.left = Node(None, parent = root)
    root.right = Node(None, parent = root)

    for val in perm:
        node = root
        while not node.is_leaf(): #find spot to place new node
            if node.value > val:  node = node.left
            else: node = node.right
        node.value = val  #change the leaf to an inner node
        node.left = Node(None, parent = node) #create new leaves
        node.right = Node(None, parent = node)
    return root

def perm_to_tree(permutation):
    """Given a list permutation, creates the tree associated with that permutation.
    Returns the tree in bracket form."""
    
    #obtains tree with leaves unlabelled
    root = perm_to_tree_structure(p)

    root.create_tokens()

    # goes through all leaf values and plays the "token game"
    for leaf in range(1, len(p)+2):
        root.place_leaf_value(leaf, permutation)

    return tree_to_bracket(root)






# tests that all trees created by permutations of 1...n are unique
"""
for n in range(1, 10): #size of permutation
    perms = permutations(list(range(1,n+1)))
    all_trees = set()
    for p in perms: #creates trees out of all permutations of 1...n
        tree = perm_to_tree(p)
        all_trees.add(tree)
    print(len(all_trees))  #prints the number of unique trees created
"""



