# DSA Advanced Q&A — Hard Interview Topics
# 35+ Questions: Hard Graphs, Advanced DP, Trees, System Design DS, Bit Manipulation, Greedy

---

## ── ADVANCED GRAPH PROBLEMS ──────────────────────────────────

**Q1: Implement Dijkstra's algorithm. When does it fail?**

A: Dijkstra finds shortest paths from a source to all other nodes in a weighted graph with **non-negative edge weights**.

```python
import heapq

def dijkstra(graph, start):
    """
    graph = {"A": [("B", 4), ("C", 1)], "C": [("B", 2)], ...}
    Returns: dict of shortest distances from start
    """
    dist = {start: 0}
    heap = [(0, start)]   # (cost, node)

    while heap:
        curr_dist, node = heapq.heappop(heap)

        # Stale entry — skip (we already found a shorter path)
        if curr_dist > dist.get(node, float('inf')):
            continue

        for neighbor, weight in graph.get(node, []):
            new_dist = curr_dist + weight
            if new_dist < dist.get(neighbor, float('inf')):
                dist[neighbor] = new_dist
                heapq.heappush(heap, (new_dist, neighbor))

    return dist

# Time: O((V + E) log V) with min-heap | Space: O(V)
```

**When Dijkstra FAILS**: negative edge weights. If a negative edge exists, Dijkstra can finalize a "shortest" distance and later discover a shorter path through the negative edge.

**Fix**: Use **Bellman-Ford** for graphs with negative weights — O(V × E) time. Bellman-Ford also detects negative weight cycles.

---

**Q2: Explain Bellman-Ford algorithm. What is a negative cycle?**

A: Bellman-Ford relaxes all edges V-1 times. After V-1 iterations, all shortest paths (which have at most V-1 edges in a V-node graph) are found.

```python
def bellman_ford(V, edges, start):
    """
    edges = [(u, v, weight), ...]
    Returns: dist array or None if negative cycle
    """
    dist = [float('inf')] * V
    dist[start] = 0

    for _ in range(V - 1):       # relax all edges V-1 times
        for u, v, w in edges:
            if dist[u] != float('inf') and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w

    # V-th relaxation: if any distance still improves → negative cycle!
    for u, v, w in edges:
        if dist[u] != float('inf') and dist[u] + w < dist[v]:
            return None   # negative cycle detected

    return dist

# Time: O(V × E) | Space: O(V)
```

A **negative cycle** is a cycle whose total edge weight is negative. If you keep traversing it, the "shortest path" would decrease to -∞ — so shortest paths are undefined.

---

**Q3: What is Floyd-Warshall? When would you use it over Dijkstra?**

A: Floyd-Warshall computes **all-pairs shortest paths** in a graph with possibly negative edges (but no negative cycles).

```python
def floyd_warshall(V, graph):
    """
    graph[i][j] = weight of edge i→j, or inf if no edge
    Returns: dist[i][j] = shortest path from i to j
    """
    dist = [row[:] for row in graph]   # make a copy

    for k in range(V):          # intermediate node
        for i in range(V):
            for j in range(V):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]

    return dist

# Time: O(V³) | Space: O(V²)
```

**Use Floyd-Warshall when**:
- You need shortest paths between ALL pairs of nodes
- Graph is dense (E ≈ V²) and V is small
- Graph may have negative edges (but no negative cycles)

**Use Dijkstra when**:
- You need shortest paths from ONE source
- All edge weights are non-negative
- Graph is sparse (E << V²)

---

**Q4: Explain Union-Find with path compression and union by rank. What problems does it solve?**

A: Union-Find (Disjoint Set Union) maintains partitions of a set. Two optimizations make it nearly O(1) per operation:

1. **Path Compression** — during `find`, make every node on the path point directly to the root
2. **Union by Rank** — always attach the shallower tree under the deeper tree to keep trees balanced

```python
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank   = [0] * n
        self.count  = n    # number of connected components

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])   # path compression
        return self.parent[x]

    def union(self, x, y):
        px, py = self.find(x), self.find(y)
        if px == py: return False     # same component → this edge creates a cycle
        if self.rank[px] < self.rank[py]: px, py = py, px
        self.parent[py] = px
        if self.rank[px] == self.rank[py]: self.rank[px] += 1
        self.count -= 1
        return True

    def connected(self, x, y):
        return self.find(x) == self.find(y)

# Time: O(α(n)) per operation — practically O(1)
```

**Solves**:
- Number of connected components
- Detect cycle in undirected graph (if `union` returns False → edge creates cycle)
- Kruskal's Minimum Spanning Tree (add edges in order of weight, skip if same component)
- Accounts merge, friend circles

---

**Q5: Implement topological sort using both DFS and BFS (Kahn's). When does it fail?**

A: Topological sort only works on **Directed Acyclic Graphs (DAGs)**.

**Kahn's Algorithm** (BFS — start from nodes with in-degree 0):
```python
from collections import deque
def topo_bfs(graph, V):
    in_degree = [0] * V
    for u in range(V):
        for v in graph[u]:
            in_degree[v] += 1
    queue  = deque([i for i in range(V) if in_degree[i] == 0])
    result = []
    while queue:
        node = queue.popleft()
        result.append(node)
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    return result if len(result) == V else []   # [] = cycle detected
```

**DFS-based** (add to result AFTER visiting all descendants — reversed postorder):
```python
def topo_dfs(graph, V):
    visited = [0] * V   # 0=unvisited, 1=in-progress, 2=done
    result  = []

    def dfs(node):
        if visited[node] == 1: return False  # back edge → cycle!
        if visited[node] == 2: return True
        visited[node] = 1
        for neighbor in graph[node]:
            if not dfs(neighbor): return False
        visited[node] = 2
        result.append(node)
        return True

    for i in range(V):
        if visited[i] == 0:
            if not dfs(i): return []   # cycle
    return result[::-1]   # reverse DFS postorder = topological order
```

**Fails**: if the graph has a cycle — Kahn's will have `len(result) < V`; DFS will detect a back edge.

---

## ── ADVANCED DYNAMIC PROGRAMMING ────────────────────────────

**Q6: 2D DP — Unique Paths. Explain the state and recurrence.**

A: Robot starts at top-left of m×n grid. Can only move right or down. How many unique paths to bottom-right?

```python
def unique_paths(m, n):
    """
    State: dp[i][j] = number of paths to reach cell (i, j)
    Recurrence: dp[i][j] = dp[i-1][j] + dp[i][j-1]
      (came from above OR from the left)
    Base case: dp[0][j] = 1 for all j (only one way along top row)
               dp[i][0] = 1 for all i (only one way along left col)
    """
    dp = [[1] * n for _ in range(m)]
    for i in range(1, m):
        for j in range(1, n):
            dp[i][j] = dp[i-1][j] + dp[i][j-1]
    return dp[m-1][n-1]

# Space optimization: use 1D array
def unique_paths_optimized(m, n):
    dp = [1] * n
    for _ in range(1, m):
        for j in range(1, n):
            dp[j] += dp[j-1]   # dp[j] was "above", dp[j-1] is "left"
    return dp[n-1]

# Time: O(m×n) | Space: O(n)
print(unique_paths(3, 7))   # 28
```

---

**Q7: String DP — Edit Distance (Levenshtein Distance)**

A: Minimum operations (insert, delete, replace) to convert word1 to word2.

```python
def edit_distance(word1, word2):
    """
    dp[i][j] = min edit distance for word1[:i] and word2[:j]

    If chars match:    dp[i][j] = dp[i-1][j-1]
    If chars differ:   dp[i][j] = 1 + min(
                                    dp[i-1][j],    # delete from word1
                                    dp[i][j-1],    # insert into word1
                                    dp[i-1][j-1]   # replace
                                  )
    Base: dp[i][0] = i (delete all of word1[:i])
          dp[0][j] = j (insert all of word2[:j])
    """
    m, n = len(word1), len(word2)
    dp   = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1): dp[i][0] = i
    for j in range(n + 1): dp[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if word1[i-1] == word2[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])
    return dp[m][n]

# Time: O(m×n) | Space: O(m×n) → O(n) with rolling array
print(edit_distance("horse", "ros"))    # 3
print(edit_distance("intention", "execution"))  # 5
```

---

**Q8: Interval DP — Burst Balloons**

A: Interval DP solves problems where subproblems are defined by a range [i, j] and you combine solutions from smaller ranges.

```python
def max_coins_burst_balloons(nums):
    """
    nums[i] = value of balloon i. Bursting i earns nums[i-1]*nums[i]*nums[i+1].
    Return max coins from bursting all balloons.

    Key insight: think of the LAST balloon to burst in range [i,j].
    dp[i][j] = max coins from bursting all balloons in (i, j) exclusive.
    """
    nums = [1] + nums + [1]   # add boundary balloons
    n    = len(nums)
    dp   = [[0] * n for _ in range(n)]

    # length of interval
    for length in range(2, n):
        for left in range(0, n - length):
            right = left + length
            for k in range(left + 1, right):   # k is last to burst
                dp[left][right] = max(
                    dp[left][right],
                    nums[left] * nums[k] * nums[right] + dp[left][k] + dp[k][right]
                )
    return dp[0][n-1]

# Time: O(n³) | Space: O(n²)
print(max_coins_burst_balloons([3, 1, 5, 8]))  # 167
```

---

**Q9: DP with bitmask — Minimum Cost to Visit All Nodes (TSP variant)**

A: Bitmask DP represents visited sets as integers. For n ≤ 20 nodes.

```python
def shortest_path_all_nodes(graph):
    """
    graph[i][j] = cost of edge i→j (-1 if no edge)
    Find shortest path that visits all nodes starting from node 0.
    State: dp[mask][node] = min cost to reach 'node' having visited set 'mask'
    """
    n    = len(graph)
    INF  = float('inf')
    full = (1 << n) - 1   # all nodes visited bitmask

    # Initialize DP
    dp = [[INF] * n for _ in range(1 << n)]
    dp[1][0] = 0   # start at node 0, visited = {0} = 0b001

    for mask in range(1 << n):
        for node in range(n):
            if dp[mask][node] == INF: continue
            if not (mask >> node & 1): continue   # node not in mask
            for neighbor in range(n):
                if mask >> neighbor & 1: continue  # already visited
                if graph[node][neighbor] == -1: continue
                new_mask = mask | (1 << neighbor)
                dp[new_mask][neighbor] = min(
                    dp[new_mask][neighbor],
                    dp[mask][node] + graph[node][neighbor]
                )

    return min(dp[full])
# Time: O(2ⁿ × n²) | Space: O(2ⁿ × n)
```

---

**Q10: Palindrome Partitioning DP — minimum cuts to make all substrings palindromes**

A:

```python
def min_cut_palindrome(s):
    """
    dp[i] = minimum cuts for s[:i+1]
    If s[j:i+1] is palindrome: dp[i] = min(dp[i], dp[j-1] + 1)
    """
    n    = len(s)
    dp   = list(range(-1, n))   # dp[i+1] for s[:i+1], base dp[0]=-1

    # Precompute palindrome table with expand-around-center
    is_pal = [[False] * n for _ in range(n)]
    for center in range(n):
        l, r = center, center
        while l >= 0 and r < n and s[l] == s[r]:
            is_pal[l][r] = True; l -= 1; r += 1
        l, r = center, center + 1
        while l >= 0 and r < n and s[l] == s[r]:
            is_pal[l][r] = True; l -= 1; r += 1

    for i in range(n):
        dp[i + 1] = dp[i] + 1   # worst case: cut before i
        for j in range(i + 1):
            if is_pal[j][i]:
                dp[i + 1] = min(dp[i + 1], dp[j] + 1)

    return dp[n] - 1   # -1 because dp counts "cuts" as segments - 1

# Time: O(n²) | Space: O(n²)
print(min_cut_palindrome("aab"))   # 1 ("aa" | "b")
```

---

## ── TREE PROBLEMS — ADVANCED ─────────────────────────────────

**Q11: What is a Segment Tree? Implement range sum query with point update.**

A: A Segment Tree is a binary tree where each node stores an aggregate (sum, min, max) over a range of array indices. Enables O(log n) range queries AND O(log n) point updates (vs O(1) query + O(n) update for prefix sums).

```python
class SegmentTree:
    """
    Range sum query + point update — O(log n) for both
    """
    def __init__(self, nums):
        self.n    = len(nums)
        self.tree = [0] * (2 * self.n)
        # Build: leaves at indices n..2n-1, internal nodes at 1..n-1
        for i in range(self.n):
            self.tree[self.n + i] = nums[i]
        for i in range(self.n - 1, 0, -1):
            self.tree[i] = self.tree[2*i] + self.tree[2*i + 1]

    def update(self, idx, val):
        """Point update: set nums[idx] = val"""
        pos = idx + self.n
        self.tree[pos] = val
        while pos > 1:
            pos //= 2
            self.tree[pos] = self.tree[2*pos] + self.tree[2*pos + 1]

    def query(self, left, right):
        """Range sum: sum(nums[left:right+1])"""
        result = 0
        left  += self.n
        right += self.n + 1
        while left < right:
            if left & 1:   result += self.tree[left];  left  += 1
            if right & 1:  right  -= 1; result += self.tree[right]
            left  //= 2
            right //= 2
        return result

st = SegmentTree([1, 3, 5, 7, 9, 11])
print(st.query(1, 3))   # 15 (3+5+7)
st.update(1, 2)
print(st.query(1, 3))   # 14 (2+5+7)
```

**Lazy propagation** extends this to O(log n) range updates (e.g., add 5 to all elements in range).

---

**Q12: Implement a Trie with autocomplete. Explain time/space complexity.**

A:

```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end   = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        """O(L) where L = word length"""
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_end = True

    def search(self, word):
        """O(L) — exact match"""
        node = self.root
        for ch in word:
            if ch not in node.children: return False
            node = node.children[ch]
        return node.is_end

    def starts_with(self, prefix):
        """O(L) — prefix check"""
        node = self.root
        for ch in prefix:
            if ch not in node.children: return False
            node = node.children[ch]
        return True

    def autocomplete(self, prefix):
        """Return all words starting with prefix — O(L + W×L)"""
        node = self.root
        for ch in prefix:
            if ch not in node.children: return []
            node = node.children[ch]
        result = []
        self._collect(node, prefix, result)
        return result

    def _collect(self, node, current, result):
        if node.is_end: result.append(current)
        for ch, child in node.children.items():
            self._collect(child, current + ch, result)

t = Trie()
for word in ["apple", "app", "application", "apply", "apt"]:
    t.insert(word)
print(t.autocomplete("app"))   # ["app", "apple", "application", "apply"]
print(t.search("apple"))       # True
print(t.starts_with("ap"))     # True
```

**Space complexity**: O(ALPHABET_SIZE × average_word_length × number_of_words)
In the worst case with no shared prefixes: O(26 × L × N).
In the best case with all words sharing prefixes: O(L_longest + branch_points).

---

**Q13: Find the diameter of a binary tree.**

A: Diameter = length of the longest path between any two nodes (path does not need to pass through root).

```python
def diameter_of_binary_tree(root):
    """
    Key: at each node, the longest path through it = left_height + right_height
    We update the global max at each node, but return height for the parent.
    O(n) time, O(h) space
    """
    max_diameter = [0]

    def height(node):
        if not node: return 0
        left  = height(node.left)
        right = height(node.right)
        max_diameter[0] = max(max_diameter[0], left + right)
        return 1 + max(left, right)

    height(root)
    return max_diameter[0]
```

Common mistake: only checking diameter through root. Must check at every node.

---

**Q14: Binary Tree Maximum Path Sum (Hard)**

A: Find the maximum path sum where the path can start and end at any node.

```python
def max_path_sum(root):
    """
    At each node, max contribution = node.val + max(0, left_gain, right_gain)
    Max path through node = node.val + max(0, left_gain) + max(0, right_gain)
    Return only one side to parent (path can't branch upward)
    O(n) time, O(h) space
    """
    max_sum = [float('-inf')]

    def gain(node):
        if not node: return 0
        left_gain  = max(0, gain(node.left))   # ignore negative contributions
        right_gain = max(0, gain(node.right))
        # Price of current path through this node
        max_sum[0] = max(max_sum[0], node.val + left_gain + right_gain)
        # Return max gain if we continue the path
        return node.val + max(left_gain, right_gain)

    gain(root)
    return max_sum[0]
```

---

## ── SYSTEM DESIGN WITH DATA STRUCTURES ──────────────────────

**Q15: Implement LFU Cache (Least Frequently Used)**

A: LFU evicts the least frequently used item. On tie, evict the least recently used among them.

```python
from collections import defaultdict, OrderedDict

class LFUCache:
    """O(1) get and put — uses frequency map + doubly linked list per frequency"""
    def __init__(self, capacity):
        self.capacity  = capacity
        self.min_freq  = 0
        self.key_val   = {}                  # key → value
        self.key_freq  = {}                  # key → frequency
        self.freq_keys = defaultdict(OrderedDict)  # freq → {key: None} ordered by recency

    def _update_freq(self, key):
        f = self.key_freq[key]
        del self.freq_keys[f][key]
        if not self.freq_keys[f] and f == self.min_freq:
            self.min_freq += 1
        self.key_freq[key] = f + 1
        self.freq_keys[f + 1][key] = None

    def get(self, key):
        if key not in self.key_val: return -1
        self._update_freq(key)
        return self.key_val[key]

    def put(self, key, value):
        if self.capacity <= 0: return
        if key in self.key_val:
            self.key_val[key] = value
            self._update_freq(key)
            return
        if len(self.key_val) >= self.capacity:
            # Evict: remove the first (oldest) key at min_freq
            evict_key, _ = self.freq_keys[self.min_freq].popitem(last=False)
            del self.key_val[evict_key]
            del self.key_freq[evict_key]
        self.key_val[key]  = value
        self.key_freq[key] = 1
        self.freq_keys[1][key] = None
        self.min_freq = 1

# All operations O(1)
lfu = LFUCache(2)
lfu.put(1, 1); lfu.put(2, 2)
print(lfu.get(1))   # 1 (freq[1]=2, freq[2]=1)
lfu.put(3, 3)       # evicts key 2 (freq 1, least recently used among min freq)
print(lfu.get(2))   # -1
print(lfu.get(3))   # 3
```

---

**Q16: Design a data structure supporting insert, delete, getRandom in O(1)**

A: Combine a HashMap (for O(1) index lookup) + dynamic array (for O(1) getRandom).

```python
import random

class RandomizedSet:
    """All operations O(1)"""
    def __init__(self):
        self.val_to_idx = {}   # value → index in nums array
        self.nums       = []   # stores values

    def insert(self, val):
        if val in self.val_to_idx: return False
        self.nums.append(val)
        self.val_to_idx[val] = len(self.nums) - 1
        return True

    def remove(self, val):
        if val not in self.val_to_idx: return False
        # Swap with last element (avoids O(n) shift)
        idx      = self.val_to_idx[val]
        last_val = self.nums[-1]
        self.nums[idx]          = last_val
        self.val_to_idx[last_val] = idx
        self.nums.pop()
        del self.val_to_idx[val]
        return True

    def get_random(self):
        return random.choice(self.nums)  # O(1) for array

rs = RandomizedSet()
rs.insert(1); rs.insert(2); rs.insert(3)
rs.remove(2)
print(rs.get_random())   # 1 or 3, uniformly at random
```

---

**Q17: Implement a Median Finder for a data stream using two heaps**

A: Maintain a max-heap (lower half) and min-heap (upper half). Balance them so sizes differ by at most 1.

```python
import heapq

class MedianFinder:
    """
    addNum: O(log n) | findMedian: O(1)
    lower: max-heap (negate values) — stores smaller half
    upper: min-heap — stores larger half
    Invariant: len(lower) >= len(upper), len(lower) - len(upper) <= 1
    """
    def __init__(self):
        self.lower = []   # max-heap (negated for Python min-heap)
        self.upper = []   # min-heap

    def add_num(self, num):
        heapq.heappush(self.lower, -num)        # push to max-heap
        # Balance: ensure every lower element ≤ every upper element
        if self.upper and -self.lower[0] > self.upper[0]:
            val = -heapq.heappop(self.lower)
            heapq.heappush(self.upper, val)
        # Rebalance sizes
        if len(self.lower) < len(self.upper):
            val = heapq.heappop(self.upper)
            heapq.heappush(self.lower, -val)
        elif len(self.lower) > len(self.upper) + 1:
            val = -heapq.heappop(self.lower)
            heapq.heappush(self.upper, val)

    def find_median(self):
        if len(self.lower) > len(self.upper):
            return -self.lower[0]           # odd total: lower has the middle
        return (-self.lower[0] + self.upper[0]) / 2.0  # even: average of two middles

mf = MedianFinder()
mf.add_num(1); mf.add_num(2)
print(mf.find_median())  # 1.5
mf.add_num(3)
print(mf.find_median())  # 2.0
```

---

**Q18: Implement a Twitter-like design: post tweet, follow, unfollow, get news feed**

A: Classic system design with data structures.

```python
from collections import defaultdict
import heapq

class Twitter:
    """
    postTweet: O(1)
    getNewsFeed: O(F log F + 10 log 10) where F = number of followees
    follow/unfollow: O(1)
    """
    def __init__(self):
        self.timestamp  = 0
        self.tweets     = defaultdict(list)   # userId → [(time, tweetId), ...]
        self.following  = defaultdict(set)    # userId → {followeeId, ...}

    def post_tweet(self, user_id, tweet_id):
        self.tweets[user_id].append((self.timestamp, tweet_id))
        self.timestamp -= 1   # decrement so latest tweet has smallest (heap-friendly)

    def get_news_feed(self, user_id):
        """Return 10 most recent tweets from user + followees"""
        heap = []
        # Add user's own tweets
        sources = {user_id} | self.following[user_id]
        for uid in sources:
            if self.tweets[uid]:
                # Push (time, tweet_id, uid, idx) — idx points to tweet position
                idx  = len(self.tweets[uid]) - 1
                time, tweet_id = self.tweets[uid][idx]
                heapq.heappush(heap, (time, tweet_id, uid, idx))

        result = []
        while heap and len(result) < 10:
            time, tweet_id, uid, idx = heapq.heappop(heap)
            result.append(tweet_id)
            if idx > 0:
                idx -= 1
                t, tid = self.tweets[uid][idx]
                heapq.heappush(heap, (t, tid, uid, idx))
        return result

    def follow(self, follower, followee):
        self.following[follower].add(followee)

    def unfollow(self, follower, followee):
        self.following[follower].discard(followee)
```

---

## ── BIT MANIPULATION ─────────────────────────────────────────

**Q19: Explain key bit manipulation operations with interview examples.**

A:

```python
# ── BIT OPERATIONS ─────────────────────────────────────────
n = 0b1010  # = 10

# Check if bit i is set
def is_set(n, i):
    return (n >> i) & 1 == 1

# Set bit i
def set_bit(n, i):
    return n | (1 << i)

# Clear bit i
def clear_bit(n, i):
    return n & ~(1 << i)

# Toggle bit i
def toggle_bit(n, i):
    return n ^ (1 << i)

# Count set bits (Brian Kernighan's algorithm)
def count_bits(n):
    count = 0
    while n:
        n &= n - 1   # clears the lowest set bit each time
        count += 1
    return count

# Power of 2 check
def is_power_of_two(n):
    return n > 0 and (n & (n - 1)) == 0

# XOR tricks
# a ^ a = 0  (XOR with itself = 0)
# a ^ 0 = a  (XOR with 0 = itself)
# XOR is commutative and associative

# ── INTERVIEW PROBLEMS ──────────────────────────────────────

# Single Number: every element appears twice except one — find it
def single_number(nums):
    """O(n) time, O(1) space — XOR all numbers"""
    result = 0
    for num in nums:
        result ^= num   # duplicates cancel out: a ^ a = 0
    return result
# [4,1,2,1,2] → 4

# Number of 1 bits (Hamming Weight)
def hamming_weight(n):
    count = 0
    while n:
        count += n & 1   # check LSB
        n >>= 1          # shift right
    return count

# Reverse bits
def reverse_bits(n):
    result = 0
    for _ in range(32):
        result = (result << 1) | (n & 1)
        n >>= 1
    return result

# Sum of two integers WITHOUT using + or -
def get_sum(a, b):
    """Using XOR for sum bits and AND for carry bits"""
    mask = 0xFFFFFFFF   # 32-bit mask
    while b & mask:
        carry = (a & b) << 1
        a     = a ^ b
        b     = carry
    return a if b == 0 else a & mask

print(single_number([4, 1, 2, 1, 2]))  # 4
print(count_bits(11))                   # 3 (1011 has three 1s)
print(is_power_of_two(16))             # True
print(is_power_of_two(10))             # False
```

---

**Q20: Find the missing number in range [0, n] using XOR**

A:

```python
def missing_number(nums):
    """
    XOR all numbers 0..n with all elements in nums.
    Present numbers cancel (a^a=0), missing number remains.
    O(n) time, O(1) space
    """
    n      = len(nums)
    result = n   # start with n (the last index)
    for i, num in enumerate(nums):
        result ^= i ^ num
    return result

# Alternative: math — expected sum - actual sum
def missing_number_math(nums):
    n = len(nums)
    return n * (n + 1) // 2 - sum(nums)

print(missing_number([3, 0, 1]))    # 2
print(missing_number([9,6,4,2,3,5,7,0,1]))  # 8
```

---

## ── GREEDY ALGORITHMS ────────────────────────────────────────

**Q21: Explain the Activity Selection (Interval Scheduling) greedy approach**

A: Given intervals, find the maximum number of non-overlapping intervals.

```python
def erase_overlap_intervals(intervals):
    """
    Greedy: sort by END time, always pick the interval ending earliest.
    If next interval starts before current end → they overlap → skip it.
    Return minimum number of REMOVALS to make them non-overlapping.
    O(n log n) time, O(1) space
    """
    if not intervals: return 0
    intervals.sort(key=lambda x: x[1])   # sort by end time
    removals = 0
    end      = intervals[0][1]
    for start, stop in intervals[1:]:
        if start < end:
            removals += 1   # overlaps — remove (keep the one ending earlier, already in)
        else:
            end = stop       # no overlap — update end
    return removals

print(erase_overlap_intervals([[1,2],[2,3],[3,4],[1,3]]))  # 1 (remove [1,3])
print(erase_overlap_intervals([[1,2],[1,2],[1,2]]))        # 2
```

**Why sort by end time?** By choosing the interval ending soonest, we leave the most room for future intervals. This is the greedy exchange argument: swapping any other choice with the earliest-ending available choice never makes the solution worse.

---

**Q22: Jump Game — can you reach the last index? (Greedy)**

A:

```python
def can_jump(nums):
    """
    Greedy: track the farthest position reachable from current position.
    If current position > farthest reachable → stuck, return False.
    O(n) time, O(1) space
    """
    farthest = 0
    for i, jump in enumerate(nums):
        if i > farthest: return False  # can't reach position i
        farthest = max(farthest, i + jump)
    return True

def jump_game_ii(nums):
    """
    Minimum jumps to reach last index (always possible per constraints).
    Greedy BFS-style: treat each jump range as a BFS level.
    O(n) time, O(1) space
    """
    jumps = 0
    current_end  = 0   # end of current jump range
    farthest     = 0   # farthest we can reach

    for i in range(len(nums) - 1):
        farthest = max(farthest, i + nums[i])
        if i == current_end:   # exhausted current level — must jump
            jumps      += 1
            current_end = farthest

    return jumps

print(can_jump([2, 3, 1, 1, 4]))  # True
print(can_jump([3, 2, 1, 0, 4]))  # False
print(jump_game_ii([2, 3, 1, 1, 4]))  # 2
```

---

**Q23: Task Scheduler — CPU scheduling with cooldown (Greedy)**

A: Given tasks A-Z with a cooldown n between same tasks, find minimum time to execute all.

```python
from collections import Counter

def least_interval(tasks, n):
    """
    Greedy: always schedule the most frequent remaining task.
    Math formula: max(len(tasks), (max_freq - 1) * (n + 1) + count_of_max_freq_tasks)
    O(n) time, O(1) space (26 distinct tasks max)
    """
    freq     = Counter(tasks)
    max_freq = max(freq.values())
    # How many tasks have max frequency?
    max_count = sum(1 for f in freq.values() if f == max_freq)

    # Minimum time = max(total tasks, formula accounting for cooldown gaps)
    return max(len(tasks), (max_freq - 1) * (n + 1) + max_count)

print(least_interval(["A","A","A","B","B","B"], 2))  # 8: ABXABXAB
print(least_interval(["A","A","A","B","B","B"], 0))  # 6: any order
```

---

**Q24: Reconstruct Itinerary (Graph + Greedy + Euler Path)**

A: Find itinerary visiting all tickets exactly once, lexicographically smallest path.

```python
from collections import defaultdict

def find_itinerary(tickets):
    """
    Hierholzer's algorithm for Euler path.
    Sort neighbors so we always try lexicographically smallest first.
    Add to result AFTER exhausting all outgoing edges from a node (postorder).
    O(E log E) time, O(E) space
    """
    graph = defaultdict(list)
    for src, dst in sorted(tickets, reverse=True):   # reverse sort for pop efficiency
        graph[src].append(dst)

    # Each adjacency list is sorted in reverse → pop() gives lexicographically smallest

    result = []
    stack  = ["JFK"]

    while stack:
        while graph[stack[-1]]:
            stack.append(graph[stack[-1]].pop())
        result.append(stack.pop())   # add when no more outgoing edges

    return result[::-1]

print(find_itinerary([["MUC","LHR"],["JFK","MUC"],["SFO","SJC"],["LHR","SFO"]]))
# ["JFK","MUC","LHR","SFO","SJC"]
```

---

## ── HARD TREE PROBLEMS ───────────────────────────────────────

**Q25: Serialize and Deserialize N-ary tree**

A:

```python
class NaryNode:
    def __init__(self, val=None, children=None):
        self.val      = val
        self.children = children or []

def serialize_nary(root):
    """BFS with level markers — O(n)"""
    if not root: return ""
    result = []
    queue  = deque([root])
    while queue:
        node = queue.popleft()
        result.append(str(node.val))
        result.append(str(len(node.children)))
        for child in node.children:
            queue.append(child)
    return ",".join(result)

def deserialize_nary(data):
    if not data: return None
    vals  = data.split(",")
    root  = NaryNode(int(vals[0]))
    queue = deque([root])
    i     = 2
    while queue:
        node = queue.popleft()
        child_count = int(vals[i - 1])
        for _ in range(child_count):
            child = NaryNode(int(vals[i]))
            i    += 1
            node.children.append(child)
            queue.append(child)
            i    += 1   # skip child's child_count
    return root
```

---

**Q26: Vertical Order Traversal of Binary Tree**

A: Collect nodes column by column, top to bottom, left to right, sorted by value within same position.

```python
from collections import defaultdict

def vertical_order(root):
    """O(n log n) time — sorting within each column"""
    if not root: return []
    col_map = defaultdict(list)

    def dfs(node, row, col):
        if not node: return
        col_map[col].append((row, node.val))
        dfs(node.left,  row + 1, col - 1)
        dfs(node.right, row + 1, col + 1)

    dfs(root, 0, 0)
    result = []
    for col in sorted(col_map.keys()):
        column = [val for row, val in sorted(col_map[col])]
        result.append(column)
    return result
```

---

**Q27: Count complete tree nodes in O(log²n)**

A: A complete binary tree has all levels full except possibly the last, filled from left.

```python
def count_nodes(root):
    """
    O(log²n) by leveraging complete tree properties.
    If left height == right height → left subtree is perfect: 2^h - 1 nodes + 1 root
    Else right subtree is perfect one level shorter → recurse on left.
    """
    if not root: return 0

    left, right = root, root
    lh = rh     = 0
    while left:  lh += 1; left  = left.left
    while right: rh += 1; right = right.right

    if lh == rh:
        return (1 << lh) - 1   # perfect binary tree: 2^h - 1

    return 1 + count_nodes(root.left) + count_nodes(root.right)

# Time: O(log n × log n) = O(log²n) | Space: O(log n) recursion
```

---

## ── ADDITIONAL HARD PROBLEMS ─────────────────────────────────

**Q28: Word Break II — find all ways to segment string using dictionary**

A: Backtracking with memoization.

```python
def word_break_ii(s, word_dict):
    """
    O(2ⁿ) worst case (each char can be a split point), O(n²) with memo
    """
    word_set = set(word_dict)
    memo     = {}

    def backtrack(start):
        if start in memo: return memo[start]
        if start == len(s): return [[]]
        result = []
        for end in range(start + 1, len(s) + 1):
            word = s[start:end]
            if word in word_set:
                for rest in backtrack(end):
                    result.append([word] + rest)
        memo[start] = result
        return result

    return [" ".join(words) for words in backtrack(0)]

print(word_break_ii("catsanddog", ["cat","cats","and","sand","dog"]))
# ["cats and dog", "cat sand dog"]
```

---

**Q29: Regular Expression Matching (DP)**

A: Implement `isMatch(s, p)` where `.` matches any char and `*` matches zero or more of preceding.

```python
def is_match_regex(s, p):
    """
    dp[i][j] = does s[:i] match p[:j]?
    If p[j-1] == '*':
      - zero occurrences: dp[i][j] = dp[i][j-2]
      - one or more:     dp[i][j] = dp[i-1][j] if s[i-1] matches p[j-2]
    Else:
      dp[i][j] = dp[i-1][j-1] if s[i-1] matches p[j-1] (char or '.')
    O(m×n) time and space
    """
    m, n = len(s), len(p)
    dp   = [[False] * (n + 1) for _ in range(m + 1)]
    dp[0][0] = True
    # Empty string can match patterns like "a*", "a*b*"
    for j in range(2, n + 1):
        if p[j - 1] == '*':
            dp[0][j] = dp[0][j - 2]

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if p[j-1] == '*':
                dp[i][j] = dp[i][j-2]   # zero of preceding
                if p[j-2] == '.' or p[j-2] == s[i-1]:
                    dp[i][j] |= dp[i-1][j]   # one or more
            elif p[j-1] == '.' or p[j-1] == s[i-1]:
                dp[i][j] = dp[i-1][j-1]

    return dp[m][n]

print(is_match_regex("aa",  "a*"))   # True
print(is_match_regex("ab",  ".*"))   # True
print(is_match_regex("aab", "c*a*b")) # True
print(is_match_regex("mississippi", "mis*is*p*.")) # False
```

---

**Q30: Alien Dictionary — infer character ordering from sorted word list**

A: Topological sort on characters.

```python
def alien_order(words):
    """
    Build a graph of character ordering constraints from adjacent words.
    Then topological sort to get valid ordering.
    O(C) where C = total characters in all words
    """
    from collections import defaultdict, deque

    # Initialize adjacency list for all unique chars
    graph     = {ch: set() for word in words for ch in word}
    in_degree = {ch: 0     for word in words for ch in word}

    for i in range(len(words) - 1):
        w1, w2  = words[i], words[i+1]
        min_len = min(len(w1), len(w2))
        # Detect invalid ordering: "abcd" before "ab" is invalid
        if len(w1) > len(w2) and w1[:min_len] == w2[:min_len]:
            return ""
        for j in range(min_len):
            if w1[j] != w2[j]:
                if w2[j] not in graph[w1[j]]:
                    graph[w1[j]].add(w2[j])
                    in_degree[w2[j]] += 1
                break

    queue  = deque([ch for ch in in_degree if in_degree[ch] == 0])
    result = []
    while queue:
        ch = queue.popleft()
        result.append(ch)
        for neighbor in graph[ch]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    return "".join(result) if len(result) == len(in_degree) else ""

print(alien_order(["wrt","wrf","er","ett","rftt"]))  # "wertf"
```

---

## ── PATTERN SUMMARY ──────────────────────────────────────────

**Q31: How do you recognize which pattern applies to a problem?**

A:

| Pattern              | When you see...                                                    |
|----------------------|--------------------------------------------------------------------|
| Two Pointers         | Sorted array, palindrome, sum/difference conditions                |
| Sliding Window       | Substring/subarray, "longest/shortest with condition"              |
| Fast/Slow Pointers   | Linked list cycle, find middle, "happy number"                     |
| Binary Search        | Sorted data, "minimum that satisfies X", answer space search       |
| DFS + Backtracking   | All combinations/permutations/subsets, word search, N-Queens       |
| BFS                  | Shortest path (unweighted), level-order, "minimum steps"           |
| Dynamic Programming  | "Min/max ways", "can you achieve X", overlapping subproblems       |
| Greedy               | "Maximum non-overlapping", scheduling, provably local optimal      |
| Topological Sort     | Task ordering, "can you complete all courses", dependency graphs   |
| Union-Find           | Connected components, cycle detection, "merge groups"              |
| Monotonic Stack      | "Next greater/smaller element", "largest rectangle"                |
| Heap/Priority Queue  | "Top K", "merge K sorted", streaming median, Dijkstra             |
| Trie                 | Prefix search, autocomplete, word existence                        |
| Segment Tree         | Range query + point update, range min/max/sum with updates        |
| Bitmask DP           | Subsets, n ≤ 20, "visit all nodes" variants                       |
