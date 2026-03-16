# DSA Q&A — Comprehensive Interview Reference
# 25+ Questions covering Big O, Data Structures, Patterns, and Tricky Interview Topics

---

## ── BIG O NOTATION ───────────────────────────────────────────

**Q1: What is Big O notation and why do we use it?**

A: Big O notation describes how the **runtime or memory usage of an algorithm GROWS as the input size n grows**. It lets us compare algorithms independently of hardware, programming language, or constants.

Key rules:
- Drop constants: O(2n) → O(n), O(100) → O(1)
- Drop lower-order terms: O(n² + n) → O(n²), O(n + log n) → O(n)
- We measure the **worst case** unless stated otherwise (e.g., "average case for Quick Sort")

Why it matters: An O(n²) algorithm on 1,000,000 elements makes 10¹² operations. An O(n log n) solution makes ~20,000,000. The difference is the gap between a program finishing in 1 second vs. 11 days.

---

**Q2: List all common Big O complexities from fastest to slowest with examples.**

A:

| Complexity | Name         | Example                                      |
|------------|--------------|----------------------------------------------|
| O(1)       | Constant     | dict/array lookup, push/pop stack            |
| O(log n)   | Logarithmic  | binary search, balanced BST operations       |
| O(√n)      | Square root  | factorization, some sieve algorithms         |
| O(n)       | Linear       | single loop, linear search                   |
| O(n log n) | Linearithmic | merge sort, heap sort, quick sort (average)  |
| O(n²)      | Quadratic    | nested loops, bubble sort, naive string match|
| O(n³)      | Cubic        | 3 nested loops, Floyd-Warshall all-pairs     |
| O(2ⁿ)      | Exponential  | fibonacci without memoization, all subsets   |
| O(n!)      | Factorial    | all permutations, traveling salesman brute   |

**Interview tip:** Always state both time AND space complexity: *"O(n) time because we iterate once. O(n) space because our hashmap holds at most n entries in the worst case."*

---

**Q3: What is amortized time complexity?**

A: The **average cost per operation over a sequence of many operations**, even if individual operations are occasionally expensive.

Classic example — Python list `append()`:
- Usually O(1): just writes to the next slot
- Occasionally O(n): the internal array is full and must double in capacity (copy all elements)
- Over n appends: total work is n + n/2 + n/4 + ... ≈ 2n → **O(1) amortized per append**

Other examples: hash table resize, deque operations.

---

**Q4: What is space complexity? How is it different from auxiliary space?**

A: **Space complexity** = total memory used by the algorithm, including input storage.

**Auxiliary space** = **extra** memory used beyond the input itself. Usually when people say "space complexity" in interviews, they mean auxiliary space.

Examples:
- `sum(arr)`: O(1) auxiliary space — just one variable
- `reverse(arr)` in-place: O(1) auxiliary space
- `reverse(arr)` with new array: O(n) auxiliary space
- Recursive DFS: O(h) space where h = recursion stack depth (tree height)
- Merge sort: O(n) for the merge buffer at each level

---

## ── DATA STRUCTURES — WHEN TO USE EACH ──────────────────────

**Q5: When should you use an array vs. a linked list?**

A:

| Use Array when...                            | Use Linked List when...                    |
|----------------------------------------------|--------------------------------------------|
| You need O(1) random access by index         | You need O(1) insert/delete at head/tail   |
| Data size is known or won't change much      | Data size changes frequently               |
| Cache performance matters (contiguous memory)| You're implementing a stack or queue       |
| You need binary search                       | You need a deque (double-ended queue)      |

**Key difference**: Arrays store data in contiguous memory → cache-friendly. Linked list nodes can be scattered → more pointer chasing, worse cache performance.

In practice: **use arrays/lists by default**. Linked lists are mainly useful for implementing stacks, queues, or systems with O(1) insert/delete at known positions (e.g., LRU cache's doubly linked list).

---

**Q6: When should you use a HashMap vs. a Set vs. a TreeMap?**

A:

| Structure | When to use                                             | Lookup    | Order       |
|-----------|---------------------------------------------------------|-----------|-------------|
| HashMap   | Key → value mapping, frequency counting, memoization   | O(1) avg  | None        |
| HashSet   | Membership testing, deduplication, "seen" tracking     | O(1) avg  | None        |
| TreeMap   | Need sorted key order, range queries, min/max key      | O(log n)  | Sorted      |
| OrderedDict (Python) | Preserve insertion order + fast lookup      | O(1) avg  | Insertion   |

**Rule of thumb**: If you just need "have I seen this before?" → use a Set. If you need to count occurrences → use a HashMap/Counter. If you need sorted keys → use a TreeMap (Python's `sortedcontainers.SortedDict`).

---

**Q7: When should you use a Stack vs. a Queue?**

A:

| Stack (LIFO)                              | Queue (FIFO)                                 |
|-------------------------------------------|----------------------------------------------|
| DFS graph/tree traversal                  | BFS graph/tree traversal                     |
| Valid parentheses / bracket matching      | Level-order tree traversal                   |
| Undo/redo history                         | Task scheduling, print queue                 |
| Monotonic stack (next greater element)    | Sliding window min/max                       |
| Function call stack, backtracking         | Shortest path in unweighted graph            |
| Expression evaluation                     | Producer-consumer problems                   |

Python: use `list` for stack (`append`/`pop`). Use `collections.deque` for queue (`append`/`popleft`). **Never use `list.pop(0)` as a queue — it is O(n)!**

---

**Q8: When should you use a Heap (Priority Queue)?**

A: Use a heap when you need **repeated access to the minimum or maximum element** without sorting everything.

Common use cases:
- **Top-K elements**: maintain a min-heap of size k → heap top = kth largest
- **Merge K sorted lists**: use min-heap with (value, list_index, element_index)
- **Dijkstra's algorithm**: always process the unvisited node with smallest distance
- **Task scheduling**: always execute highest priority task
- **Median of a stream**: two heaps (max-heap for lower half, min-heap for upper half)

Python: `heapq` is a min-heap. Negate values for max-heap. `heappush` and `heappop` are O(log n). `heapify` converts a list to a heap in O(n).

---

**Q9: When should you use a Trie vs. a HashMap for string problems?**

A:

| Use Trie when...                                    | Use HashMap when...                        |
|-----------------------------------------------------|-------------------------------------------|
| Need to search by PREFIX ("autocomplete")           | Need exact key lookup                     |
| Large common prefixes (saves memory vs. full keys) | Words share no common prefixes            |
| Need "starts_with" queries                          | Frequency counting of exact strings       |
| IP routing (longest prefix matching)                | Anagram checking (sorted key trick)       |

Trie operations: O(L) per insert/search/prefix where L = word length.
HashMap with full words: O(L) average per operation (hashing the key).
**Trie wins when prefix queries are needed.** HashMap wins for simple exact lookups.

---

## ── COMMON INTERVIEW PATTERNS ────────────────────────────────

**Q10: What is the Two Pointers technique? Give three use cases.**

A: Use **two index variables** (usually `left` and `right`, or `slow` and `fast`) to traverse data with a single pass, reducing O(n²) solutions to O(n).

**Variant 1 — Opposite ends** (sorted arrays):
```python
# Pair with target sum in sorted array
left, right = 0, len(arr) - 1
while left < right:
    s = arr[left] + arr[right]
    if s == target: return [left, right]
    elif s < target: left += 1    # need bigger number
    else:            right -= 1   # need smaller number
```

**Variant 2 — Same direction** (fast/slow):
```python
# Remove duplicates from sorted array in-place
slow = 0
for fast in range(1, len(nums)):
    if nums[fast] != nums[slow]:
        slow += 1
        nums[slow] = nums[fast]
return slow + 1
```

**Variant 3 — Fast/Slow pointers** (linked list cycle detection — Floyd's algorithm):
```python
slow = fast = head
while fast and fast.next:
    slow = slow.next
    fast = fast.next.next
    if slow == fast: return True  # cycle!
```

Three key use cases: palindrome checking, removing duplicates in-place, cycle detection in linked lists.

---

**Q11: What is the Sliding Window technique? Fixed vs. Variable window?**

A: Maintain a contiguous range `[left, right]` and slide it through the input. Add new element on the right, remove old element on the left. Avoids recomputing the entire window each time: O(n) instead of O(n²).

**Fixed window** (window size = k is constant):
```python
def max_sum_k(arr, k):
    window_sum = sum(arr[:k])
    max_sum    = window_sum
    for i in range(k, len(arr)):
        window_sum += arr[i]       # add incoming
        window_sum -= arr[i - k]   # remove outgoing
        max_sum = max(max_sum, window_sum)
    return max_sum
```

**Variable window** (shrink window when condition violated):
```python
def longest_no_repeat(s):
    char_pos = {}
    left = max_len = 0
    for right, char in enumerate(s):
        if char in char_pos and char_pos[char] >= left:
            left = char_pos[char] + 1   # shrink past duplicate
        char_pos[char] = right
        max_len = max(max_len, right - left + 1)
    return max_len
```

Use sliding window whenever the problem asks about **subarrays or substrings** with some property (sum ≤ k, no duplicate characters, all characters of t present, etc.).

---

**Q12: Explain BFS vs. DFS and when to use each.**

A:

| Aspect              | BFS                                    | DFS                                     |
|---------------------|----------------------------------------|-----------------------------------------|
| Data structure      | Queue (FIFO)                           | Stack / recursion                       |
| Space complexity    | O(w) — w = max width of tree/graph    | O(h) — h = max depth of recursion      |
| Finds shortest path?| YES — in unweighted graphs             | No (not guaranteed)                     |
| Use cases           | Shortest path, level-order traversal, nearest neighbor | Topological sort, all paths, cycle detection, backtracking |

```python
# BFS — use a queue, explore level by level
from collections import deque
def bfs(graph, start):
    visited = {start}
    queue   = deque([start])
    while queue:
        node = queue.popleft()
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

# DFS — use recursion (or explicit stack), go deep first
def dfs(graph, node, visited=set()):
    visited.add(node)
    for neighbor in graph[node]:
        if neighbor not in visited:
            dfs(graph, neighbor, visited)
```

**Interview rule**: Need shortest path in unweighted graph → BFS. Need to find all paths, detect cycles, or enumerate solutions → DFS.

---

**Q13: What is Dynamic Programming? What are the two approaches?**

A: Dynamic Programming = **break a problem into overlapping subproblems, solve each subproblem once, store and reuse results**.

Applicability: optimal substructure + overlapping subproblems.

**Approach 1 — Top-Down Memoization** (recursion + cache):
```python
from functools import lru_cache
@lru_cache(maxsize=None)
def fib(n):
    if n <= 1: return n
    return fib(n-1) + fib(n-2)
# Natural to write. O(n) time, O(n) space (call stack + cache)
```

**Approach 2 — Bottom-Up Tabulation** (iterative DP):
```python
def fib(n):
    if n <= 1: return n
    dp = [0] * (n + 1)
    dp[1] = 1
    for i in range(2, n + 1):
        dp[i] = dp[i-1] + dp[i-2]
    return dp[n]
# No recursion stack. Can often optimize space further.
```

**When to use DP**: The problem asks for "minimum", "maximum", "number of ways", "can you achieve X" — and smaller subproblems overlap.

Classic DP problems: Fibonacci, Climbing Stairs, Coin Change, Knapsack, LCS, LIS, Edit Distance.

---

**Q14: What is Backtracking? How does it differ from DFS?**

A: Backtracking is a **DFS that explores all possibilities and UNDOES choices (backtracks) when a path fails**. Used when you need to enumerate or find all valid combinations.

```python
def permutations(nums):
    result = []
    def backtrack(path, remaining):
        if not remaining:
            result.append(path[:])   # found valid solution — add copy
            return
        for i, num in enumerate(remaining):
            path.append(num)                         # make choice
            backtrack(path, remaining[:i] + remaining[i+1:])  # explore
            path.pop()                               # undo choice (BACKTRACK)
    backtrack([], nums)
    return result
# [1,2,3] → [[1,2,3],[1,3,2],[2,1,3],[2,3,1],[3,1,2],[3,2,1]]
```

DFS explores a fixed graph. Backtracking builds the "graph" (decision tree) dynamically and prunes branches early.

Common backtracking problems: Permutations, Combinations, Subsets, N-Queens, Word Search, Sudoku Solver.

---

**Q15: Explain the Binary Search pattern for "search in answer space".**

A: Binary search isn't just for sorted arrays. You can binary search on the **answer itself** when:
1. There is a monotonic function: if answer X works, then X+1 also works (or vice versa)
2. You can define a `canSolve(mid)` check efficiently

```python
# "Koko Eating Bananas" — find minimum eating speed
def min_eating_speed(piles, h):
    import math
    def can_finish(speed):
        return sum(math.ceil(p / speed) for p in piles) <= h

    left, right = 1, max(piles)
    while left < right:
        mid = (left + right) // 2
        if can_finish(mid): right = mid       # mid works, try smaller
        else:               left  = mid + 1   # too slow, need bigger
    return left
# Time: O(n log(max_pile))
```

Template: define `left`, `right` as the valid answer range. Binary search on this range with a feasibility check. When `left == right`, that's the answer.

---

**Q16: What is the "Fast and Slow Pointer" technique?**

A: Two pointers move through the sequence at different speeds (typically 1 step and 2 steps). When they meet in a cycle, the slow pointer has traveled half the distance the fast pointer has.

Uses:
1. **Detect cycle in linked list** — fast and slow meet inside the cycle
2. **Find cycle start** — after detection, reset one pointer to head; both advance 1 step until they meet = cycle start
3. **Find middle of linked list** — when fast reaches end, slow is at middle
4. **Happy number** — detect cycle in number sequence
5. **Find duplicate number** — Floyd's algorithm on index-as-pointer

```python
# Find middle — classic interview snippet
def find_middle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    return slow   # slow is the middle when fast reaches end
```

---

## ── CLASSIC ALGORITHM QUESTIONS ──────────────────────────────

**Q17: Two Sum — explain the optimal solution and its trade-offs.**

A: **Brute force**: try all pairs — O(n²) time, O(1) space.
**Optimal**: HashMap — O(n) time, O(n) space.

```python
def two_sum(nums, target):
    seen = {}   # value → index
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []
```

Trade-off: we use O(n) extra space to avoid the second O(n) loop. This is the classic "space for time" trade-off. The interview answer should always state: *"O(n) time because we make one pass. O(n) space because the hashmap can store at most n elements."*

---

**Q18: Valid Parentheses — why a stack? What edge cases exist?**

A: A stack is perfect because bracket matching is **Last In First Out** — the most recently opened bracket must be closed first.

```python
def is_valid(s):
    stack = []
    pairs = {")": "(", "}": "{", "]": "["}
    for char in s:
        if char in "({[":
            stack.append(char)
        else:
            if not stack or stack[-1] != pairs[char]:
                return False
            stack.pop()
    return len(stack) == 0
```

Edge cases: empty string (True), string with only closers ")" (False — empty stack), unclosed openers "(((" (False — non-empty stack at end), single character "(" (False).

---

**Q19: Best Time to Buy and Sell Stock — why not use two pointers?**

A: Two pointers on a sorted array for "pair sum" works because the array is sorted. Stock prices are unsorted — a larger price might appear before a smaller price.

The correct insight: for each price, the best profit is `price - min_price_so_far`. One forward pass is sufficient.

```python
def max_profit(prices):
    min_price = float('inf')
    max_profit = 0
    for price in prices:
        min_price  = min(min_price, price)
        max_profit = max(max_profit, price - min_price)
    return max_profit
```

O(n) time, O(1) space. The key insight is that buying and selling are not symmetric — we must buy BEFORE selling, so we track the minimum seen from the LEFT only.

---

**Q20: Explain Kadane's Algorithm for Maximum Subarray.**

A: At each position, we have a local decision: **extend the previous subarray or start a brand new one here**.

```python
current_sum = max(num, current_sum + num)
```

If `current_sum + num < num`, then the previous subarray hurts us — start fresh. Otherwise extend.

All-negative array: the algorithm still works because it initializes with `nums[0]` and naturally picks the least-negative element.

Pitfall: do NOT initialize `max_sum = 0` — that would wrongly return 0 for all-negative inputs.

---

**Q21: When would you use a greedy algorithm vs. dynamic programming?**

A:

**Greedy**: Make the locally optimal choice at each step, never revisit decisions. Works when the **greedy choice property** holds — a globally optimal solution can be built from locally optimal choices.

Examples: Activity Selection (sort by end time, always pick earliest finishing), Huffman Coding, Dijkstra's (greedy on shortest distance), fractional knapsack.

**DP**: When greedy fails because past choices affect future options. Use when subproblems overlap and you need to try multiple options to find the global optimum.

Examples: 0/1 Knapsack (greedy fails — can't split items), Coin Change (greedy fails — [1,3,4] target 6: greedy picks 4→1+1 = 3 coins; optimal is 3+3 = 2 coins), LCS, Edit Distance.

**Interview test**: Does the greedy choice at each step ALWAYS lead to the global optimum? If you can prove it (by exchange argument) → greedy. If not → DP.

---

**Q22: What is topological sort and how do you implement it?**

A: Topological sort produces a **linear ordering of nodes in a Directed Acyclic Graph (DAG)** such that for every edge u → v, u appears before v.

**When to use**: course scheduling, build dependency order, task ordering.

**Kahn's Algorithm** (BFS-based):
```python
from collections import deque
def topo_sort(graph):
    in_degree = {n: 0 for n in graph}
    for node in graph:
        for neighbor in graph[node]:
            in_degree[neighbor] += 1

    queue  = deque([n for n in in_degree if in_degree[n] == 0])
    result = []
    while queue:
        node = queue.popleft()
        result.append(node)
        for neighbor in graph.get(node, []):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    # If len(result) != num_nodes → cycle exists → impossible to sort
    return result
```

Time: O(V + E) | Space: O(V)

---

**Q23: Explain Union-Find and when to use it.**

A: Union-Find (Disjoint Set Union) tracks a collection of sets. Supports:
- `find(x)`: which set does x belong to? (returns root/representative)
- `union(x, y)`: merge the sets containing x and y

With **path compression** + **union by rank**: nearly O(1) per operation (O(α(n)) where α is inverse Ackermann — grows so slowly it's practically constant).

```python
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank   = [0] * n

    def find(self, x):           # path compression
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x, y):       # union by rank
        px, py = self.find(x), self.find(y)
        if px == py: return False   # same set → cycle detected!
        if self.rank[px] < self.rank[py]: px, py = py, px
        self.parent[py] = px
        if self.rank[px] == self.rank[py]: self.rank[px] += 1
        return True
```

Use cases: detecting cycles in undirected graphs, Kruskal's MST, number of connected components, accounts merge problem.

---

**Q24: How do you explain a solution's complexity during an interview?**

A: Follow this template — state BOTH time and space, explain WHY:

*"My solution is **O(n) time** because we make a single pass through the array, doing constant-time work at each step — the hashmap lookup and insertion are both O(1).*

*The **space complexity is O(n)** because in the worst case, we add every element to the hashmap before finding the answer — for example, if the answer is the last pair."*

Bad answer: "It's O(n)." (Doesn't say time vs space, doesn't explain why)

Good answer: Explains time, explains space, calls out the worst case, optionally discusses trade-offs vs. the brute-force approach.

---

**Q25: What are the most common mistakes in coding interviews?**

A:

1. **Not clarifying the problem first** — ask about constraints (array size, negative numbers, duplicates, empty input)

2. **Not handling edge cases** — empty array, single element, all same values, negative numbers, null pointers

3. **Jumping to code before thinking** — say your approach out loud first; interviewers want to see your thought process

4. **Starting with the optimal solution** — first show brute force, THEN optimize. It shows you understand the problem.

5. **Forgetting that dict/set lookups are O(1)** — a common missed optimization is replacing a list scan with a set lookup

6. **Off-by-one errors** — especially in binary search (`left <= right` vs `left < right`), and window bounds

7. **Not testing your code** — mentally run through at least one example and one edge case after writing the solution

8. **Incorrect space complexity** — forgetting to count the recursion call stack (which is O(h) for tree/graph DFS)
