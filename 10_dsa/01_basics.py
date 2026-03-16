# ============================================================
# DSA BASICS — Complete Data Structures & Algorithms Reference
# ============================================================
# Topics: Big O, Arrays, HashMaps, Stacks, Queues, Sets,
#         Linked Lists, Trees, Heaps, Graphs, Tries,
#         Two Pointers, Sliding Window, Fast/Slow Pointers

# ── BIG O NOTATION ───────────────────────────────────────────
# Measures how runtime or memory GROWS as input size n grows
# Rule: drop constants and lower-order terms
# O(2n) → O(n)   |   O(n + 100) → O(n)   |   O(n² + n) → O(n²)
#
# Complexity hierarchy (fastest → slowest):
# O(1) < O(log n) < O(√n) < O(n) < O(n log n) < O(n²) < O(n³) < O(2ⁿ) < O(n!)

# O(1) — CONSTANT — speed does not depend on input size
def get_first(lst):
    return lst[0]           # direct index access — always one step

my_dict = {"a": 1}
val = my_dict["a"]          # hash table lookup — O(1) average

# O(log n) — LOGARITHMIC — halves the problem each step
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:    return mid
        elif arr[mid] < target:   left  = mid + 1   # discard left half
        else:                     right = mid - 1   # discard right half
    return -1
# 1,000,000 elements → only ~20 iterations (log₂ 1,000,000 ≈ 20)

# O(n) — LINEAR — one pass through all n elements
def find_max(lst):
    max_val = lst[0]
    for item in lst:            # visits every element once
        if item > max_val:
            max_val = item
    return max_val

# O(n log n) — divide-and-conquer algorithms
# Achieved by: merge sort, heap sort, quick sort (average)
# Cannot sort a general comparison-based array faster than O(n log n)

# O(n²) — QUADRATIC — nested loops over the same input
def bubble_sort(lst):
    n = len(lst)
    for i in range(n):
        for j in range(n - i - 1):      # inner loop shrinks but still O(n) average
            if lst[j] > lst[j + 1]:
                lst[j], lst[j + 1] = lst[j + 1], lst[j]
    return lst

# O(2ⁿ) — EXPONENTIAL — doubles with each extra element
def fib_naive(n):
    if n <= 1: return n
    return fib_naive(n - 1) + fib_naive(n - 2)   # branches into 2 subproblems

# O(n!) — FACTORIAL — permutations, worst possible
# Travelling salesman brute force: try all n! orderings

# ── SPACE-TIME COMPLEXITY TRADE-OFFS ─────────────────────────
# Key insight: you can often trade MORE SPACE for LESS TIME
#
# Example — check if array has duplicate:
#   Brute force: O(n²) time, O(1) space  (nested loops)
#   HashMap:     O(n)  time, O(n) space  (use space to gain speed)
#
# Example — memoization (cache computed results):
#   Fib naive:   O(2ⁿ) time, O(n) stack space
#   Fib + memo:  O(n)  time, O(n) space   (trade space for huge time gain)
#
# Rule of thumb in interviews: O(n) extra space is almost always acceptable
# to bring O(n²) time down to O(n) time.

# ── ARRAYS / LISTS ────────────────────────────────────────────
# Python list = dynamic array backed by contiguous memory
# Access by index:    O(1)  — direct memory address calculation
# Append to end:      O(1)  amortized (doubles capacity when full)
# Insert at index i:  O(n)  — must shift elements i..end right
# Delete at index i:  O(n)  — must shift elements i+1..end left
# Search by value:    O(n)  — must scan each element

lst = [3, 1, 4, 1, 5, 9, 2, 6]
lst.append(7)           # O(1)
lst.insert(0, 0)        # O(n) — shifts everything right
lst.pop()               # O(1) — remove last
lst.pop(0)              # O(n) — shifts everything left
lst.index(5)            # O(n) — linear scan
lst.sort()              # O(n log n) — Timsort in-place
sorted_lst = sorted(lst)  # O(n log n) — new sorted copy
lst.reverse()           # O(n)
len(lst)                # O(1) — Python stores length separately

# List comprehensions — same O complexity, cleaner syntax
squares = [x * x for x in range(10)]        # O(n)
evens   = [x for x in range(20) if x % 2 == 0]  # O(n)

# ── HASHMAP / DICT ────────────────────────────────────────────
# Hash table: hashes key → array index for O(1) average access
# Get/Set/Delete/Contains: O(1) average, O(n) worst (rare collision)
# Space: O(n)

d = {}
d["key"] = "value"          # O(1) set
val = d.get("key", None)    # O(1) get with default
"key" in d                  # O(1) membership check
del d["key"]                # O(1) delete

from collections import defaultdict, Counter, OrderedDict

freq = Counter("aababcc")   # Counter({'a': 3, 'b': 2, 'c': 2})
freq.most_common(2)         # [('a', 3), ('b', 2)]

groups = defaultdict(list)  # auto-initializes missing keys with []
groups["fruits"].append("apple")

# ── SET ──────────────────────────────────────────────────────
# Hash table storing only keys (no values)
# Add/Remove/Contains: O(1) average
# No duplicates — deduplicate a list instantly

seen = set()
seen.add(5)             # O(1)
5 in seen               # O(1) — MUCH faster than list "in" which is O(n)
seen.discard(5)         # O(1) — no error if not present

nums = [1, 2, 2, 3, 3, 3]
unique = list(set(nums))    # [1, 2, 3] deduplicated — O(n)

# Set operations
a, b = {1, 2, 3}, {2, 3, 4}
a & b   # intersection {2, 3} — O(min(len(a), len(b)))
a | b   # union {1, 2, 3, 4} — O(len(a) + len(b))
a - b   # difference {1}     — O(len(a))

# ── STACK — LIFO (Last In First Out) ─────────────────────────
# Python list used as stack: append() = push, pop() = pop — both O(1)
# Use cases: matching brackets, undo/redo, DFS, expression evaluation,
#            function call stack, monotonic stack problems

stack = []
stack.append(1)     # push 1
stack.append(2)     # push 2
stack.append(3)     # push 3  → stack = [1, 2, 3]
top  = stack[-1]    # peek top = 3  (O(1), no removal)
top  = stack.pop()  # pop  top = 3  → stack = [1, 2]

# MONOTONIC STACK — keeps elements in increasing or decreasing order
# Used for: next greater element, largest rectangle in histogram
def next_greater_element(nums):
    """For each element find the next greater element to its right"""
    result = [-1] * len(nums)
    stack  = []   # stores indices, not values
    for i, num in enumerate(nums):
        while stack and nums[stack[-1]] < num:
            idx = stack.pop()
            result[idx] = num       # num is next greater for idx
        stack.append(i)
    return result
# [2, 1, 4, 3] → [4, 4, -1, -1]

# ── QUEUE — FIFO (First In First Out) ────────────────────────
# Use collections.deque — O(1) append and popleft
# NEVER use list.pop(0) as a queue — it is O(n)!
# Use cases: BFS traversal, level-order tree traversal, task scheduling

from collections import deque

queue = deque()
queue.append(1)           # enqueue right — O(1)
queue.appendleft(0)       # enqueue left  — O(1)
front = queue[0]          # peek front    — O(1)
front = queue.popleft()   # dequeue left  — O(1)
back  = queue.pop()       # dequeue right — O(1)

# ── LINKED LIST ───────────────────────────────────────────────
# Series of nodes where each node holds data + pointer to next
# Access by index:  O(n) — must traverse from head
# Insert at head:   O(1)
# Insert at tail:   O(1) if tail pointer kept, O(n) otherwise
# Delete by value:  O(n) — must find node first
# Search:           O(n)
# Advantage over array: O(1) insert/delete at known position (no shifting)

class ListNode:
    def __init__(self, val=0, next=None):
        self.val  = val
        self.next = next

# Build: 1 → 2 → 3 → None
head = ListNode(1, ListNode(2, ListNode(3)))

# Traverse
def print_list(head):
    curr = head
    while curr:
        print(curr.val, end=" → ")
        curr = curr.next
    print("None")

# Reverse a singly linked list — O(n) time, O(1) space
def reverse_list(head):
    prev, curr = None, head
    while curr:
        next_node   = curr.next   # save next
        curr.next   = prev        # reverse pointer
        prev        = curr        # advance prev
        curr        = next_node   # advance curr
    return prev   # new head

# Detect cycle — Floyd's Tortoise and Hare — O(n) time, O(1) space
def has_cycle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next        # 1 step
        fast = fast.next.next   # 2 steps
        if slow == fast:
            return True         # met → cycle exists
    return False

# Find middle of linked list — O(n) time, O(1) space
def find_middle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    return slow   # slow is at middle when fast reaches end

# DOUBLY LINKED LIST — each node has prev and next pointers
class DoublyListNode:
    def __init__(self, val=0):
        self.val  = val
        self.prev = None
        self.next = None

class DoublyLinkedList:
    def __init__(self):
        # Use sentinel head and tail to simplify boundary conditions
        self.head = DoublyListNode(0)   # dummy head
        self.tail = DoublyListNode(0)   # dummy tail
        self.head.next = self.tail
        self.tail.prev = self.head

    def add_to_front(self, node):
        """Insert node right after head sentinel — O(1)"""
        node.next       = self.head.next
        node.prev       = self.head
        self.head.next.prev = node
        self.head.next  = node

    def remove(self, node):
        """Remove any node given a pointer to it — O(1)"""
        node.prev.next = node.next
        node.next.prev = node.prev

    def remove_last(self):
        """Remove and return the last real node (before tail sentinel) — O(1)"""
        if self.tail.prev == self.head:
            return None
        last = self.tail.prev
        self.remove(last)
        return last

# ── BINARY TREE ───────────────────────────────────────────────
# Each node has at most 2 children (left and right)
# Height h:
#   - Perfect binary tree: h = log₂(n)  → operations O(log n)
#   - Skewed tree (worst case): h = n   → operations O(n)

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val   = val
        self.left  = left
        self.right = right

# Build:     4
#           / \
#          2   6
#         / \ / \
#        1  3 5  7
root = TreeNode(4,
    TreeNode(2, TreeNode(1), TreeNode(3)),
    TreeNode(6, TreeNode(5), TreeNode(7)))

# TREE TRAVERSALS (all O(n) time, O(h) space where h = height)
def inorder(root):
    """Left → Root → Right — gives SORTED order for BST"""
    if not root: return []
    return inorder(root.left) + [root.val] + inorder(root.right)

def preorder(root):
    """Root → Left → Right — used to COPY or SERIALIZE tree"""
    if not root: return []
    return [root.val] + preorder(root.left) + preorder(root.right)

def postorder(root):
    """Left → Right → Root — used to DELETE tree, evaluate expressions"""
    if not root: return []
    return postorder(root.left) + postorder(root.right) + [root.val]

def level_order(root):
    """BFS — level by level — use a queue"""
    if not root: return []
    result, queue = [], deque([root])
    while queue:
        level = []
        for _ in range(len(queue)):       # process one entire level
            node = queue.popleft()
            level.append(node.val)
            if node.left:  queue.append(node.left)
            if node.right: queue.append(node.right)
        result.append(level)
    return result

def max_depth(root):
    """DFS — height of tree — O(n) time"""
    if not root: return 0
    return 1 + max(max_depth(root.left), max_depth(root.right))

# ── BINARY SEARCH TREE (BST) ──────────────────────────────────
# BST property: left.val < node.val < right.val (all nodes in subtrees)
# Search/Insert/Delete: O(log n) average, O(n) worst (skewed tree)
# Inorder traversal of BST → sorted array

def bst_search(root, target):
    """O(log n) average — leverages BST property"""
    if not root:              return None
    if root.val == target:    return root
    elif target < root.val:   return bst_search(root.left, target)
    else:                     return bst_search(root.right, target)

def bst_insert(root, val):
    """Insert while maintaining BST property"""
    if not root: return TreeNode(val)
    if val < root.val:
        root.left  = bst_insert(root.left, val)
    elif val > root.val:
        root.right = bst_insert(root.right, val)
    return root

def is_valid_bst(root, min_val=float('-inf'), max_val=float('inf')):
    """Validate BST — every node must satisfy its valid range"""
    if not root: return True
    if not (min_val < root.val < max_val): return False
    return (is_valid_bst(root.left,  min_val, root.val) and
            is_valid_bst(root.right, root.val, max_val))

def lowest_common_ancestor_bst(root, p, q):
    """LCA in BST — O(log n) by using BST property"""
    while root:
        if p.val < root.val and q.val < root.val:
            root = root.left       # both in left subtree
        elif p.val > root.val and q.val > root.val:
            root = root.right      # both in right subtree
        else:
            return root            # split point = LCA
    return None

# ── HEAP / PRIORITY QUEUE ─────────────────────────────────────
# Complete binary tree maintained in heap order
# MIN-HEAP: parent ≤ children → root is always the MINIMUM
# MAX-HEAP: parent ≥ children → root is always the MAXIMUM
# Insert:    O(log n) — sift up
# Delete min/max: O(log n) — sift down
# Peek min/max:   O(1)
# Build heap from array: O(n)  ← surprisingly not O(n log n)
# Use cases: Dijkstra, top-k elements, merge k sorted lists, scheduling

import heapq

# Python heapq is a MIN-HEAP
min_heap = []
heapq.heappush(min_heap, 5)
heapq.heappush(min_heap, 1)
heapq.heappush(min_heap, 3)
smallest = heapq.heappop(min_heap)   # 1 — always pops minimum
peek     = min_heap[0]               # O(1) peek without removing

# MAX-HEAP: negate values (Python trick)
max_heap = []
heapq.heappush(max_heap, -5)
heapq.heappush(max_heap, -1)
heapq.heappush(max_heap, -3)
largest = -heapq.heappop(max_heap)   # 5

# heapify: convert list to heap in O(n) — more efficient than n pushes
nums = [3, 1, 4, 1, 5, 9, 2, 6]
heapq.heapify(nums)     # O(n)

# Find k largest elements — O(n log k) time, O(k) space
def find_k_largest(nums, k):
    return heapq.nlargest(k, nums)

# Find k smallest elements — O(n log k) time, O(k) space
def find_k_smallest(nums, k):
    return heapq.nsmallest(k, nums)

# Push to heap with tuple for priority with tiebreaker
tasks = []
heapq.heappush(tasks, (1, "low priority task"))
heapq.heappush(tasks, (0, "urgent task"))
priority, task = heapq.heappop(tasks)   # (0, "urgent task")

# ── GRAPH ─────────────────────────────────────────────────────
# Nodes (vertices) connected by edges
# Directed: edges have direction (A → B)
# Undirected: edges are bidirectional (A — B)
# Weighted: edges have costs/distances
# Unweighted: all edges have equal weight

# ADJACENCY LIST — best for sparse graphs O(V + E) space
graph_list = {
    "A": ["B", "C"],
    "B": ["D"],
    "C": ["D", "E"],
    "D": [],
    "E": []
}

# ADJACENCY MATRIX — best for dense graphs O(V²) space
# graph[i][j] = 1 means edge from i to j
V = 5
graph_matrix = [[0] * V for _ in range(V)]
graph_matrix[0][1] = 1   # edge 0 → 1
graph_matrix[0][2] = 1   # edge 0 → 2

# GRAPH DFS — explore as deep as possible before backtracking
# Time: O(V + E) | Space: O(V) for visited set + O(V) recursion stack
def dfs(graph, node, visited=None):
    if visited is None: visited = set()
    visited.add(node)
    print(node, end=" ")
    for neighbor in graph.get(node, []):
        if neighbor not in visited:
            dfs(graph, neighbor, visited)
    return visited

# Iterative DFS using explicit stack
def dfs_iterative(graph, start):
    visited = set()
    stack   = [start]
    order   = []
    while stack:
        node = stack.pop()
        if node not in visited:
            visited.add(node)
            order.append(node)
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    stack.append(neighbor)
    return order

# GRAPH BFS — explore level by level (shortest path in unweighted graph)
# Time: O(V + E) | Space: O(V) for queue and visited set
def bfs(graph, start):
    visited = {start}
    queue   = deque([start])
    order   = []
    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return order

# BFS SHORTEST PATH — returns distance to all reachable nodes
def bfs_shortest_path(graph, start):
    dist  = {start: 0}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        for neighbor in graph.get(node, []):
            if neighbor not in dist:
                dist[neighbor] = dist[node] + 1
                queue.append(neighbor)
    return dist

# DIJKSTRA'S ALGORITHM — shortest path in weighted graph (non-negative weights)
# Time: O((V + E) log V) with min-heap | Space: O(V)
def dijkstra(graph_weighted, start):
    """
    graph_weighted = {"A": [("B", 4), ("C", 1)], "B": [("D", 1)], ...}
    Returns dict of shortest distances from start to every node
    """
    dist = {start: 0}
    heap = [(0, start)]   # (distance, node)

    while heap:
        curr_dist, node = heapq.heappop(heap)

        if curr_dist > dist.get(node, float('inf')):
            continue   # already found a shorter path, skip

        for neighbor, weight in graph_weighted.get(node, []):
            new_dist = curr_dist + weight
            if new_dist < dist.get(neighbor, float('inf')):
                dist[neighbor] = new_dist
                heapq.heappush(heap, (new_dist, neighbor))

    return dist

# Example weighted graph
weighted_graph = {
    "A": [("B", 4), ("C", 1)],
    "B": [("D", 1)],
    "C": [("B", 2), ("D", 5)],
    "D": []
}
# dijkstra(weighted_graph, "A") → {"A": 0, "C": 1, "B": 3, "D": 4}

# TOPOLOGICAL SORT — linear ordering of vertices in a DAG
# (Directed Acyclic Graph) so that for every edge u→v, u comes before v
# Use case: task scheduling, build systems, course prerequisites
def topological_sort(graph):
    """Kahn's Algorithm (BFS-based) — O(V + E)"""
    in_degree = {node: 0 for node in graph}
    for node in graph:
        for neighbor in graph[node]:
            in_degree[neighbor] = in_degree.get(neighbor, 0) + 1

    queue  = deque([n for n in in_degree if in_degree[n] == 0])
    result = []
    while queue:
        node = queue.popleft()
        result.append(node)
        for neighbor in graph.get(node, []):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    return result if len(result) == len(graph) else []   # [] = cycle detected

# UNION-FIND (Disjoint Set Union) — O(α(n)) ≈ O(1) per operation
# Used for: detecting cycles, Kruskal's MST, connected components
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))    # each node is its own parent
        self.rank   = [0] * n           # tree height hint

    def find(self, x):
        """Find root with PATH COMPRESSION"""
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])   # flatten tree
        return self.parent[x]

    def union(self, x, y):
        """Merge two sets — UNION BY RANK to keep tree balanced"""
        px, py = self.find(x), self.find(y)
        if px == py: return False    # already in same set → cycle!
        if self.rank[px] < self.rank[py]: px, py = py, px
        self.parent[py] = px
        if self.rank[px] == self.rank[py]: self.rank[px] += 1
        return True

    def connected(self, x, y):
        return self.find(x) == self.find(y)

# ── TRIE (PREFIX TREE) ────────────────────────────────────────
# Tree where each path from root to node represents a prefix
# Insert/Search/StartsWith: O(L) where L = length of word
# Space: O(ALPHABET_SIZE × L × N) where N = number of words
# Use cases: autocomplete, spell check, IP routing, prefix matching

class TrieNode:
    def __init__(self):
        self.children = {}      # char → TrieNode
        self.is_end   = False   # marks end of a complete word

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        """O(L) — traverse/create nodes for each character"""
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True

    def search(self, word):
        """O(L) — returns True only if complete word exists"""
        node = self.root
        for char in word:
            if char not in node.children: return False
            node = node.children[char]
        return node.is_end

    def starts_with(self, prefix):
        """O(L) — returns True if any word starts with prefix"""
        node = self.root
        for char in prefix:
            if char not in node.children: return False
            node = node.children[char]
        return True

    def get_words_with_prefix(self, prefix):
        """Return all words starting with prefix — O(L + W×L)"""
        node = self.root
        for char in prefix:
            if char not in node.children: return []
            node = node.children[char]
        result = []
        self._dfs(node, prefix, result)
        return result

    def _dfs(self, node, current, result):
        if node.is_end: result.append(current)
        for char, child in node.children.items():
            self._dfs(child, current + char, result)

# ── TWO POINTERS PATTERN ─────────────────────────────────────
# Two index variables traversing the data — reduces O(n²) to O(n)
# Variants:
#   1. Opposite ends → move toward each other (palindrome, sorted pair sum)
#   2. Same direction → one leads the other (remove duplicates, remove element)
#   3. Different arrays → merge pattern

def is_palindrome(s):
    """Two pointers from both ends — O(n) time, O(1) space"""
    left, right = 0, len(s) - 1
    while left < right:
        if s[left] != s[right]: return False
        left  += 1
        right -= 1
    return True

def two_sum_sorted(arr, target):
    """Only works on SORTED arrays — O(n) time, O(1) space"""
    left, right = 0, len(arr) - 1
    while left < right:
        total = arr[left] + arr[right]
        if total == target:   return [left, right]
        elif total < target:  left  += 1   # need bigger
        else:                 right -= 1   # need smaller
    return []

def remove_duplicates_sorted(nums):
    """Remove in-place from sorted array — O(n) time, O(1) space"""
    if not nums: return 0
    slow = 0
    for fast in range(1, len(nums)):
        if nums[fast] != nums[slow]:
            slow += 1
            nums[slow] = nums[fast]
    return slow + 1   # new length

# ── SLIDING WINDOW PATTERN ────────────────────────────────────
# Maintain a window [left, right] and slide it through the input
# Fixed window: window size = k (constant)
# Variable window: window size changes based on condition

def max_sum_subarray(nums, k):
    """Fixed window — O(n) time, O(1) space"""
    window_sum = sum(nums[:k])
    max_sum    = window_sum
    for i in range(k, len(nums)):
        window_sum += nums[i]       # add right element
        window_sum -= nums[i - k]   # remove left element
        max_sum = max(max_sum, window_sum)
    return max_sum

def longest_substring_no_repeat(s):
    """Variable window — O(n) time, O(min(n, 26)) space"""
    char_pos = {}   # char → last seen index
    left     = 0
    max_len  = 0
    for right, char in enumerate(s):
        if char in char_pos and char_pos[char] >= left:
            left = char_pos[char] + 1   # shrink window past duplicate
        char_pos[char] = right
        max_len = max(max_len, right - left + 1)
    return max_len

def min_window_substring(s, t):
    """Find minimum window in s containing all chars of t — O(n)"""
    from collections import Counter
    need    = Counter(t)
    missing = len(t)
    left    = 0
    result  = ""
    for right, char in enumerate(s):
        if need[char] > 0:
            missing -= 1
        need[char] -= 1
        if missing == 0:   # valid window found — try to shrink
            while need[s[left]] < 0:
                need[s[left]] += 1
                left += 1
            window = s[left:right + 1]
            if not result or len(window) < len(result):
                result = window
            need[s[left]] += 1
            missing += 1
            left    += 1
    return result

# ── FAST / SLOW POINTERS (Floyd's Algorithm) ──────────────────
# Two pointers move at different speeds through the sequence
# Slow: moves 1 step | Fast: moves 2 steps
# When they meet → cycle exists
# Use cases: detect cycle, find cycle start, find middle of list

def find_cycle_start(head):
    """Find where cycle begins — O(n) time, O(1) space"""
    slow = fast = head
    # Phase 1: detect cycle
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow == fast:
            break
    else:
        return None   # no cycle

    # Phase 2: find cycle start
    slow = head
    while slow != fast:
        slow = slow.next
        fast = fast.next
    return slow   # meeting point = cycle start

# ── COMPLEXITY CHEAT SHEET ────────────────────────────────────
# Data Structure      | Access | Search | Insert | Delete | Space
# --------------------|--------|--------|--------|--------|------
# Array               | O(1)   | O(n)   | O(n)   | O(n)   | O(n)
# Linked List         | O(n)   | O(n)   | O(1)*  | O(1)*  | O(n)
# Hash Map / Set      | -      | O(1)†  | O(1)†  | O(1)†  | O(n)
# Binary Search Tree  | O(log n)† | O(log n)† | O(log n)† | O(log n)† | O(n)
# Min/Max Heap        | O(1)** | O(n)   | O(log n)| O(log n)| O(n)
# Trie                | O(L)   | O(L)   | O(L)   | O(L)   | O(N×L)
#
# *  = at head/tail if pointer available
# †  = average case; O(n) worst case (collisions / unbalanced tree)
# ** = only for min/max, not arbitrary elements
# L  = word length, N = number of words
#
# Algorithm          | Best     | Average  | Worst    | Space
# -------------------|----------|----------|----------|-------
# Binary Search      | O(1)     | O(log n) | O(log n) | O(1)
# Bubble Sort        | O(n)     | O(n²)    | O(n²)    | O(1)
# Merge Sort         | O(nlogn) | O(nlogn) | O(nlogn) | O(n)
# Quick Sort         | O(nlogn) | O(nlogn) | O(n²)    | O(log n)
# Heap Sort          | O(nlogn) | O(nlogn) | O(nlogn) | O(1)
# BFS / DFS          | O(V+E)   | O(V+E)   | O(V+E)   | O(V)
# Dijkstra           | -        | O((V+E)log V)| -    | O(V)

print("01_basics.py loaded — all data structures and patterns defined")
