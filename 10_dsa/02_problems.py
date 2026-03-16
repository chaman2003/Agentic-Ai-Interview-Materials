# ============================================================
# DSA PROBLEMS — Python Solutions — 30 Interview Problems
# ============================================================
# Format per problem:
#   - Problem statement + examples
#   - Approach explanation (brute → optimal)
#   - Time / Space complexity
#   - Clean solution code + test cases

from collections import defaultdict, deque, Counter
import heapq
import math


# ── PROBLEM 1: TWO SUM ───────────────────────────────────────
# Given a list and a target, return indices of two numbers that sum to target.
# Input: nums=[2,7,11,15], target=9  → Output: [0,1]  (2+7=9)
# Constraints: exactly one solution, cannot use same element twice
#
# Approach:
#   Brute: try every pair → O(n²)
#   Optimal: hashmap storing value→index; for each num check if
#            complement (target-num) was already seen → O(n)

def two_sum(nums, target):
    """O(n) time, O(n) space"""
    seen = {}   # value → index
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []

print(two_sum([2, 7, 11, 15], 9))   # [0, 1]
print(two_sum([3, 2, 4], 6))        # [1, 2]
print(two_sum([3, 3], 6))           # [0, 1]


# ── PROBLEM 2: VALID PARENTHESES ─────────────────────────────
# Given a string of brackets, return True if all brackets are properly closed.
# Input: "()[]{}"  → True
# Input: "([)]"    → False   (wrong nesting order)
# Input: "{[]}"    → True
#
# Approach: Stack. Push opening brackets; for closing brackets, pop and verify
#           the top was the matching opener. Empty stack at end = valid.

def is_valid_parentheses(s):
    """O(n) time, O(n) space"""
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

print(is_valid_parentheses("()[]{}"))  # True
print(is_valid_parentheses("([)]"))    # False
print(is_valid_parentheses("{[]}"))    # True
print(is_valid_parentheses(""))        # True
print(is_valid_parentheses(")"))       # False


# ── PROBLEM 3: BEST TIME TO BUY AND SELL STOCK ───────────────
# Given prices array, find max profit from one buy + one sell.
# Must buy before you sell. Return 0 if no profit possible.
# Input: [7,1,5,3,6,4] → 5  (buy at 1, sell at 6)
# Input: [7,6,4,3,1]   → 0  (prices always falling)
#
# Approach: One-pass — track min price seen so far; at each step compute
#           potential profit (current price - min so far) and update best.

def max_profit(prices):
    """O(n) time, O(1) space"""
    min_price  = float('inf')
    best_profit = 0
    for price in prices:
        if price < min_price:
            min_price = price
        elif price - min_price > best_profit:
            best_profit = price - min_price
    return best_profit

print(max_profit([7, 1, 5, 3, 6, 4]))  # 5
print(max_profit([7, 6, 4, 3, 1]))     # 0
print(max_profit([1, 2]))              # 1


# ── PROBLEM 4: MAXIMUM SUBARRAY (Kadane's Algorithm) ─────────
# Find contiguous subarray with the largest sum.
# Input: [-2,1,-3,4,-1,2,1,-5,4] → 6  (subarray [4,-1,2,1])
#
# Approach: At each index, decide — extend previous subarray or start fresh?
#   current = max(num, current + num)
#   Optimal decision made locally at each step → O(n) time.

def max_subarray(nums):
    """Kadane's Algorithm — O(n) time, O(1) space"""
    max_sum     = nums[0]
    current_sum = nums[0]
    for num in nums[1:]:
        current_sum = max(num, current_sum + num)
        max_sum     = max(max_sum, current_sum)
    return max_sum

print(max_subarray([-2, 1, -3, 4, -1, 2, 1, -5, 4]))  # 6
print(max_subarray([1]))                                 # 1
print(max_subarray([-1, -2, -3]))                        # -1


# ── PROBLEM 5: CLIMBING STAIRS (Dynamic Programming) ─────────
# You can climb 1 or 2 steps at a time. How many distinct ways to reach step n?
# Input: n=2 → 2  (1+1, 2)
# Input: n=3 → 3  (1+1+1, 1+2, 2+1)
#
# Approach: DP — ways(n) = ways(n-1) + ways(n-2)
#   Same recurrence as Fibonacci! Use bottom-up DP with O(1) space.

def climb_stairs(n):
    """O(n) time, O(1) space — Fibonacci variant"""
    if n <= 2: return n
    prev2, prev1 = 1, 2
    for _ in range(3, n + 1):
        prev2, prev1 = prev1, prev1 + prev2
    return prev1

print(climb_stairs(2))   # 2
print(climb_stairs(3))   # 3
print(climb_stairs(5))   # 8
print(climb_stairs(10))  # 89


# ── PROBLEM 6: COIN CHANGE (Dynamic Programming) ─────────────
# Given coin denominations and an amount, return the minimum number of coins
# needed to make up the amount. Return -1 if impossible.
# Input: coins=[1,5,11], amount=15 → 3  (5+5+5) note: NOT greedy — 11+? fails
# Input: coins=[2], amount=3       → -1
#
# Approach: Bottom-up DP — dp[i] = min coins to make amount i
#   For each amount from 1 to target, try every coin and take the min.

def coin_change(coins, amount):
    """O(amount × len(coins)) time, O(amount) space"""
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0   # base case: 0 coins needed for amount 0
    for i in range(1, amount + 1):
        for coin in coins:
            if coin <= i:
                dp[i] = min(dp[i], dp[i - coin] + 1)
    return dp[amount] if dp[amount] != float('inf') else -1

print(coin_change([1, 5, 6, 9], 11))  # 2 (5+6)
print(coin_change([1, 5, 11], 15))    # 3 (5+5+5, NOT 11+1+1+1+1)
print(coin_change([2], 3))            # -1
print(coin_change([1], 0))            # 0


# ── PROBLEM 7: LONGEST COMMON SUBSEQUENCE (DP) ───────────────
# Find length of the longest subsequence present in both strings.
# A subsequence maintains relative order but not necessarily contiguous.
# Input: text1="abcde", text2="ace" → 3  ("ace")
# Input: text1="abc",   text2="abc" → 3
# Input: text1="abc",   text2="def" → 0
#
# Approach: 2D DP — dp[i][j] = LCS of text1[:i] and text2[:j]
#   If chars match: dp[i][j] = dp[i-1][j-1] + 1
#   Else:           dp[i][j] = max(dp[i-1][j], dp[i][j-1])

def longest_common_subsequence(text1, text2):
    """O(m×n) time, O(m×n) space"""
    m, n = len(text1), len(text2)
    dp   = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i - 1] == text2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[m][n]

print(longest_common_subsequence("abcde", "ace"))   # 3
print(longest_common_subsequence("abc", "abc"))     # 3
print(longest_common_subsequence("abc", "def"))     # 0


# ── PROBLEM 8: 0/1 KNAPSACK (DP) ─────────────────────────────
# Given weights and values for n items and a capacity W, find the max value
# you can fit. Each item can be taken at most once.
# weights=[2,3,4,5], values=[3,4,5,6], W=5 → 7 (items 0+1: weight 5, value 7)
#
# Approach: dp[i][w] = max value using first i items with capacity w
#   Include item i: dp[i-1][w-weight[i]] + value[i]
#   Exclude item i: dp[i-1][w]
#   Take the max.

def knapsack(weights, values, capacity):
    """O(n×W) time, O(n×W) space"""
    n  = len(weights)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for w in range(capacity + 1):
            # Don't take item i-1
            dp[i][w] = dp[i - 1][w]
            # Take item i-1 (if it fits)
            if weights[i - 1] <= w:
                dp[i][w] = max(dp[i][w], dp[i - 1][w - weights[i - 1]] + values[i - 1])
    return dp[n][capacity]

print(knapsack([2, 3, 4, 5], [3, 4, 5, 6], 5))   # 7
print(knapsack([1, 2, 3], [1, 6, 10], 5))         # 16 (items 1+2)


# ── PROBLEM 9: HOUSE ROBBER (DP) ─────────────────────────────
# Rob houses along a street; cannot rob two adjacent houses.
# Maximize total amount robbed.
# Input: [1,2,3,1] → 4  (rob house 0 and 2: 1+3)
# Input: [2,7,9,3,1] → 12  (rob houses 0,2,4: 2+9+1)
#
# Approach: dp[i] = max money robbing houses 0..i
#   Either rob house i (skip i-1) or skip house i (take dp[i-1])
#   dp[i] = max(nums[i] + dp[i-2], dp[i-1])
#   Optimize to O(1) space with two variables.

def house_robber(nums):
    """O(n) time, O(1) space"""
    if not nums: return 0
    if len(nums) == 1: return nums[0]
    prev2, prev1 = 0, 0
    for num in nums:
        prev2, prev1 = prev1, max(prev1, prev2 + num)
    return prev1

print(house_robber([1, 2, 3, 1]))      # 4
print(house_robber([2, 7, 9, 3, 1]))   # 12
print(house_robber([2, 1]))            # 2


# ── PROBLEM 10: NUMBER OF ISLANDS (Graph BFS/DFS) ────────────
# Count the number of islands in a 2D grid.
# '1' = land, '0' = water. Islands are connected horizontally/vertically.
# Input:
#   [["1","1","0"],
#    ["0","1","0"],
#    ["0","0","1"]]  → 2
#
# Approach: DFS/BFS from each unvisited land cell, marking all connected
#           land as visited (flood fill). Count how many times we start DFS.

def num_islands(grid):
    """O(m×n) time, O(m×n) space"""
    if not grid: return 0
    rows, cols = len(grid), len(grid[0])
    count = 0

    def dfs(r, c):
        if r < 0 or r >= rows or c < 0 or c >= cols or grid[r][c] != "1":
            return
        grid[r][c] = "0"   # mark visited by sinking the land
        dfs(r + 1, c); dfs(r - 1, c)
        dfs(r, c + 1); dfs(r, c - 1)

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "1":
                dfs(r, c)
                count += 1
    return count

grid1 = [["1","1","0"],["0","1","0"],["0","0","1"]]
grid2 = [["1","1","1"],["0","1","0"],["1","1","1"]]
print(num_islands(grid1))  # 2
print(num_islands(grid2))  # 1


# ── PROBLEM 11: COURSE SCHEDULE (Topological Sort / Cycle Detection) ──
# Given n courses and prerequisites pairs, can you finish all courses?
# If prerequisites contain a cycle → impossible.
# Input: n=2, prerequisites=[[1,0]] → True  (take 0 then 1)
# Input: n=2, prerequisites=[[1,0],[0,1]] → False  (cycle!)
#
# Approach: Build directed graph; use Kahn's BFS topological sort.
#   If all nodes are processed → no cycle → True. Else False.

def can_finish(num_courses, prerequisites):
    """O(V+E) time, O(V+E) space"""
    graph     = defaultdict(list)
    in_degree = [0] * num_courses

    for course, prereq in prerequisites:
        graph[prereq].append(course)
        in_degree[course] += 1

    queue    = deque([i for i in range(num_courses) if in_degree[i] == 0])
    finished = 0

    while queue:
        node = queue.popleft()
        finished += 1
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    return finished == num_courses

print(can_finish(2, [[1, 0]]))           # True
print(can_finish(2, [[1, 0], [0, 1]]))   # False
print(can_finish(4, [[1,0],[2,0],[3,1],[3,2]]))  # True


# ── PROBLEM 12: MERGE INTERVALS ──────────────────────────────
# Merge all overlapping intervals.
# Input: [[1,3],[2,6],[8,10],[15,18]] → [[1,6],[8,10],[15,18]]
# Input: [[1,4],[4,5]]               → [[1,5]]
#
# Approach: Sort by start time. For each interval, either merge with the last
#           in result (if overlapping) or add as new interval.

def merge_intervals(intervals):
    """O(n log n) time (sort), O(n) space"""
    intervals.sort(key=lambda x: x[0])
    merged = [intervals[0]]
    for start, end in intervals[1:]:
        if start <= merged[-1][1]:               # overlaps with last
            merged[-1][1] = max(merged[-1][1], end)  # extend end
        else:
            merged.append([start, end])
    return merged

print(merge_intervals([[1,3],[2,6],[8,10],[15,18]]))  # [[1,6],[8,10],[15,18]]
print(merge_intervals([[1,4],[4,5]]))                  # [[1,5]]
print(merge_intervals([[1,4],[0,4]]))                  # [[0,4]]


# ── PROBLEM 13: WORD SEARCH (Backtracking) ───────────────────
# Given a 2D board of characters, find if a word exists in the grid.
# Characters must be adjacent (horizontal/vertical), and each cell used once.
# Input: board=[["A","B","C"],["S","F","C"],["A","D","E"]], word="ABCCED" → True
#
# Approach: DFS backtracking from each starting cell. Mark visited cells
#           temporarily to avoid reuse; restore on backtrack.

def word_search(board, word):
    """O(m×n×4^L) time where L=len(word), O(L) space for recursion"""
    rows, cols = len(board), len(board[0])

    def dfs(r, c, idx):
        if idx == len(word):  return True
        if r < 0 or r >= rows or c < 0 or c >= cols: return False
        if board[r][c] != word[idx]: return False

        temp        = board[r][c]
        board[r][c] = "#"   # mark visited

        found = (dfs(r+1,c,idx+1) or dfs(r-1,c,idx+1) or
                 dfs(r,c+1,idx+1) or dfs(r,c-1,idx+1))

        board[r][c] = temp  # restore — backtrack
        return found

    for r in range(rows):
        for c in range(cols):
            if dfs(r, c, 0):
                return True
    return False

board = [["A","B","C","E"],["S","F","C","S"],["A","D","E","E"]]
print(word_search(board, "ABCCED"))  # True
print(word_search(board, "SEE"))     # True
print(word_search(board, "ABCB"))    # False


# ── PROBLEM 14: BINARY SEARCH VARIATIONS ─────────────────────
# Standard binary search — O(log n)
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = left + (right - left) // 2   # prevents integer overflow
        if arr[mid] == target:    return mid
        elif arr[mid] < target:   left  = mid + 1
        else:                     right = mid - 1
    return -1

# Find leftmost (first) occurrence of target
def binary_search_left(arr, target):
    """Returns index of first occurrence, or -1"""
    left, right = 0, len(arr) - 1
    result = -1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            result = mid
            right  = mid - 1   # keep searching left
        elif arr[mid] < target: left  = mid + 1
        else:                   right = mid - 1
    return result

# Find rightmost (last) occurrence of target
def binary_search_right(arr, target):
    left, right = 0, len(arr) - 1
    result = -1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            result = mid
            left   = mid + 1   # keep searching right
        elif arr[mid] < target: left  = mid + 1
        else:                   right = mid - 1
    return result

# Search in rotated sorted array — O(log n)
def search_rotated(nums, target):
    """[4,5,6,7,0,1,2], target=0 → 4"""
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == target: return mid
        # Left half is sorted
        if nums[left] <= nums[mid]:
            if nums[left] <= target < nums[mid]:
                right = mid - 1
            else:
                left = mid + 1
        else:   # Right half is sorted
            if nums[mid] < target <= nums[right]:
                left = mid + 1
            else:
                right = mid - 1
    return -1

arr = [1, 1, 2, 2, 3, 4, 5]
print(binary_search(arr, 2))        # 2 or 3
print(binary_search_left(arr, 2))   # 2 (first 2)
print(binary_search_right(arr, 2))  # 3 (last 2)
print(search_rotated([4,5,6,7,0,1,2], 0))  # 4


# ── PROBLEM 15: MERGE SORT ────────────────────────────────────
# Divide-and-conquer sort. Split array in half, sort each half, merge.
# Stable sort — maintains relative order of equal elements.
# Time: O(n log n) all cases | Space: O(n) for merge step

def merge_sort(arr):
    """O(n log n) time, O(n) space"""
    if len(arr) <= 1: return arr
    mid   = len(arr) // 2
    left  = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return _merge(left, right)

def _merge(left, right):
    result = []
    i = j  = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result

print(merge_sort([38, 27, 43, 3, 9, 82, 10]))  # [3, 9, 10, 27, 38, 43, 82]


# ── PROBLEM 16: QUICK SORT ────────────────────────────────────
# Divide-and-conquer sort. Pick a pivot, partition array around it.
# In-place — O(1) extra space (ignoring recursion stack).
# Average O(n log n), worst O(n²) if pivot always picks min/max.

def quick_sort(arr, low=0, high=None):
    """O(n log n) average, O(n²) worst | Space: O(log n) stack average"""
    if high is None: high = len(arr) - 1
    if low < high:
        pivot_idx = _partition(arr, low, high)
        quick_sort(arr, low, pivot_idx - 1)
        quick_sort(arr, pivot_idx + 1, high)
    return arr

def _partition(arr, low, high):
    """Lomuto partition — pivot = last element"""
    pivot = arr[high]
    i     = low - 1   # boundary of elements ≤ pivot
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1

print(quick_sort([10, 7, 8, 9, 1, 5]))  # [1, 5, 7, 8, 9, 10]


# ── PROBLEM 17: REVERSE LINKED LIST ──────────────────────────
# Reverse a singly linked list iteratively and recursively.
# Input: 1→2→3→4→5 → Output: 5→4→3→2→1

class ListNode:
    def __init__(self, val=0, next=None):
        self.val  = val
        self.next = next

def list_to_nodes(vals):
    if not vals: return None
    head = ListNode(vals[0])
    curr = head
    for v in vals[1:]:
        curr.next = ListNode(v); curr = curr.next
    return head

def nodes_to_list(head):
    result = []
    while head:
        result.append(head.val); head = head.next
    return result

def reverse_list(head):
    """Iterative — O(n) time, O(1) space"""
    prev, curr = None, head
    while curr:
        next_node = curr.next
        curr.next = prev
        prev      = curr
        curr      = next_node
    return prev   # new head

def reverse_list_recursive(head, prev=None):
    """Recursive — O(n) time, O(n) space (call stack)"""
    if not head: return prev
    next_node  = head.next
    head.next  = prev
    return reverse_list_recursive(next_node, head)

head = list_to_nodes([1, 2, 3, 4, 5])
print(nodes_to_list(reverse_list(head)))            # [5,4,3,2,1]
head2 = list_to_nodes([1, 2, 3, 4, 5])
print(nodes_to_list(reverse_list_recursive(head2))) # [5,4,3,2,1]


# ── PROBLEM 18: DETECT CYCLE IN LINKED LIST ──────────────────
# Given head of linked list, return True if it has a cycle.
# A cycle exists if some node's next pointer points to a previous node.
#
# Approach: Floyd's Cycle Detection (fast/slow pointers).
#   Slow moves 1 step, fast moves 2 steps.
#   If they ever meet → cycle. If fast reaches None → no cycle.

def has_cycle(head):
    """O(n) time, O(1) space — Floyd's algorithm"""
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow == fast:
            return True
    return False

# Build a cycle: 1→2→3→4 with 4.next = 2
n1, n2, n3, n4 = ListNode(1), ListNode(2), ListNode(3), ListNode(4)
n1.next = n2; n2.next = n3; n3.next = n4; n4.next = n2  # cycle!
print(has_cycle(n1))                           # True
print(has_cycle(list_to_nodes([1, 2, 3])))     # False


# ── PROBLEM 19: FIND KTH LARGEST ELEMENT ─────────────────────
# Find the kth largest element in an unsorted array.
# Input: nums=[3,2,1,5,6,4], k=2 → 5
#
# Approach 1: Sort descending → O(n log n)
# Approach 2: Min-heap of size k — maintains k largest elements.
#   When heap > k, pop the smallest. Heap top = kth largest. O(n log k)
# Approach 3: QuickSelect — O(n) average, O(n²) worst

def find_kth_largest(nums, k):
    """Min-heap approach — O(n log k) time, O(k) space"""
    heap = []
    for num in nums:
        heapq.heappush(heap, num)
        if len(heap) > k:
            heapq.heappop(heap)   # remove the smallest
    return heap[0]   # smallest of the k largest = kth largest

def find_kth_largest_quickselect(nums, k):
    """QuickSelect — O(n) average time, O(1) space"""
    target = len(nums) - k   # index of kth largest in sorted order

    def partition(left, right):
        pivot = nums[right]
        store = left
        for i in range(left, right):
            if nums[i] <= pivot:
                nums[i], nums[store] = nums[store], nums[i]
                store += 1
        nums[store], nums[right] = nums[right], nums[store]
        return store

    left, right = 0, len(nums) - 1
    while left <= right:
        pivot_idx = partition(left, right)
        if pivot_idx == target:    return nums[pivot_idx]
        elif pivot_idx < target:   left  = pivot_idx + 1
        else:                      right = pivot_idx - 1

print(find_kth_largest([3, 2, 1, 5, 6, 4], 2))            # 5
print(find_kth_largest_quickselect([3, 2, 3, 1, 2, 4, 5, 5, 6], 4))  # 4


# ── PROBLEM 20: VALIDATE BST ─────────────────────────────────
# Determine if a binary tree is a valid BST.
# BST property: all left subtree values < root < all right subtree values.
# Input: [2,1,3] → True
# Input: [5,1,4,null,null,3,6] → False (4 in right subtree but 4 < 5)
#
# Approach: Pass valid range [min_val, max_val] to each node.
#   Each node's value must be within this range.

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val   = val
        self.left  = left
        self.right = right

def is_valid_bst(root, min_val=float('-inf'), max_val=float('inf')):
    """O(n) time, O(h) space where h=tree height"""
    if not root: return True
    if not (min_val < root.val < max_val): return False
    return (is_valid_bst(root.left,  min_val, root.val) and
            is_valid_bst(root.right, root.val, max_val))

valid_bst   = TreeNode(2, TreeNode(1), TreeNode(3))
invalid_bst = TreeNode(5, TreeNode(1), TreeNode(4, TreeNode(3), TreeNode(6)))
print(is_valid_bst(valid_bst))    # True
print(is_valid_bst(invalid_bst))  # False (4 is in right subtree but 4 < 5)


# ── PROBLEM 21: MAX DEPTH OF BINARY TREE ─────────────────────
# Return the maximum depth (height) of a binary tree.
# Input: [3,9,20,null,null,15,7] → 3
#
# Approach: DFS recursion — depth = 1 + max(left depth, right depth)
# BFS: level-order traversal, count levels.

def max_depth(root):
    """DFS — O(n) time, O(h) space"""
    if not root: return 0
    return 1 + max(max_depth(root.left), max_depth(root.right))

def max_depth_bfs(root):
    """BFS — O(n) time, O(w) space where w=max width"""
    if not root: return 0
    queue, depth = deque([root]), 0
    while queue:
        for _ in range(len(queue)):
            node = queue.popleft()
            if node.left:  queue.append(node.left)
            if node.right: queue.append(node.right)
        depth += 1
    return depth

tree = TreeNode(3, TreeNode(9), TreeNode(20, TreeNode(15), TreeNode(7)))
print(max_depth(tree))      # 3
print(max_depth_bfs(tree))  # 3


# ── PROBLEM 22: INORDER TRAVERSAL ────────────────────────────
# Return inorder traversal (Left→Root→Right) of binary tree.
# For BST: inorder gives sorted ascending order.
# Input: [1,null,2,3] → [1,3,2]
#
# Approach 1: Recursive — clean but O(h) call stack space.
# Approach 2: Iterative with explicit stack — avoids recursion limit.

def inorder_recursive(root):
    """O(n) time, O(h) space"""
    result = []
    def traverse(node):
        if not node: return
        traverse(node.left)
        result.append(node.val)
        traverse(node.right)
    traverse(root)
    return result

def inorder_iterative(root):
    """O(n) time, O(h) space — explicit stack"""
    result, stack = [], []
    curr = root
    while curr or stack:
        while curr:               # go as far left as possible
            stack.append(curr)
            curr = curr.left
        curr = stack.pop()        # process node
        result.append(curr.val)
        curr = curr.right         # then explore right
    return result

bst = TreeNode(4, TreeNode(2, TreeNode(1), TreeNode(3)), TreeNode(6, TreeNode(5), TreeNode(7)))
print(inorder_recursive(bst))    # [1, 2, 3, 4, 5, 6, 7]
print(inorder_iterative(bst))    # [1, 2, 3, 4, 5, 6, 7]


# ── PROBLEM 23: LCA OF BST ───────────────────────────────────
# Find the Lowest Common Ancestor (LCA) of two nodes in a BST.
# LCA: lowest node in tree that has both p and q as descendants.
# Input: root=[6,2,8,0,4,7,9], p=2, q=8 → 6
# Input: root=[6,2,8,0,4,7,9], p=2, q=4 → 2
#
# Approach: Use BST property. If both p and q are less than root → go left.
#           If both greater → go right. Otherwise root is the LCA.

def lowest_common_ancestor(root, p, q):
    """O(log n) average, O(1) space — uses BST property"""
    while root:
        if p.val < root.val and q.val < root.val:
            root = root.left
        elif p.val > root.val and q.val > root.val:
            root = root.right
        else:
            return root
    return None

# For general binary tree (not BST) — O(n) time
def lca_general(root, p, q):
    """O(n) time, O(h) space — works for any binary tree"""
    if not root or root == p or root == q: return root
    left  = lca_general(root.left,  p, q)
    right = lca_general(root.right, p, q)
    if left and right: return root   # p in left, q in right → root is LCA
    return left or right             # both on same side

root_bst = TreeNode(6, TreeNode(2, TreeNode(0), TreeNode(4)), TreeNode(8, TreeNode(7), TreeNode(9)))
p_node = root_bst.left          # node with val 2
q_node = root_bst.right         # node with val 8
lca = lowest_common_ancestor(root_bst, p_node, q_node)
print(lca.val)  # 6


# ── PROBLEM 24: SERIALIZE AND DESERIALIZE BINARY TREE ────────
# Design an algorithm to serialize (encode) a binary tree to a string
# and deserialize (decode) back to a tree structure.
# Input: [1,2,3,null,null,4,5] → "1,2,3,X,X,4,5" → [1,2,3,null,null,4,5]
#
# Approach: BFS / level-order serialization.
#   Serialize: BFS, append "X" for null nodes.
#   Deserialize: BFS, use queue to assign children.

def serialize(root):
    """O(n) time, O(n) space"""
    if not root: return "X"
    queue  = deque([root])
    result = []
    while queue:
        node = queue.popleft()
        if node:
            result.append(str(node.val))
            queue.append(node.left)
            queue.append(node.right)
        else:
            result.append("X")
    return ",".join(result)

def deserialize(data):
    """O(n) time, O(n) space"""
    if data == "X": return None
    vals   = data.split(",")
    root   = TreeNode(int(vals[0]))
    queue  = deque([root])
    i      = 1
    while queue and i < len(vals):
        node = queue.popleft()
        if vals[i] != "X":
            node.left = TreeNode(int(vals[i]))
            queue.append(node.left)
        i += 1
        if i < len(vals) and vals[i] != "X":
            node.right = TreeNode(int(vals[i]))
            queue.append(node.right)
        i += 1
    return root

tree_s  = TreeNode(1, TreeNode(2), TreeNode(3, TreeNode(4), TreeNode(5)))
encoded = serialize(tree_s)
decoded = deserialize(encoded)
print(encoded)                    # "1,2,3,X,X,4,5"
print(inorder_recursive(decoded)) # [2, 1, 4, 3, 5]


# ── PROBLEM 25: SPIRAL MATRIX ─────────────────────────────────
# Given an m×n matrix, return all elements in spiral order.
# Input: [[1,2,3],[4,5,6],[7,8,9]] → [1,2,3,6,9,8,7,4,5]
#
# Approach: Maintain four boundaries (top, bottom, left, right).
#           Peel off the outer layer each iteration — shrink boundaries inward.

def spiral_order(matrix):
    """O(m×n) time, O(m×n) space for result"""
    result = []
    top, bottom = 0, len(matrix) - 1
    left, right = 0, len(matrix[0]) - 1

    while top <= bottom and left <= right:
        # Left to right along top row
        for c in range(left, right + 1):
            result.append(matrix[top][c])
        top += 1

        # Top to bottom along right column
        for r in range(top, bottom + 1):
            result.append(matrix[r][right])
        right -= 1

        # Right to left along bottom row (if rows remain)
        if top <= bottom:
            for c in range(right, left - 1, -1):
                result.append(matrix[bottom][c])
            bottom -= 1

        # Bottom to top along left column (if cols remain)
        if left <= right:
            for r in range(bottom, top - 1, -1):
                result.append(matrix[r][left])
            left += 1

    return result

print(spiral_order([[1,2,3],[4,5,6],[7,8,9]]))         # [1,2,3,6,9,8,7,4,5]
print(spiral_order([[1,2,3,4],[5,6,7,8],[9,10,11,12]])) # [1,2,3,4,8,12,11,10,9,5,6,7]


# ── PROBLEM 26: LONGEST INCREASING SUBSEQUENCE (DP) ──────────
# Find the length of the longest strictly increasing subsequence.
# Input: [10,9,2,5,3,7,101,18] → 4  ([2,3,7,101])
# Input: [0,1,0,3,2,3] → 4
#
# Approach 1: DP — dp[i] = LIS ending at index i.  O(n²)
# Approach 2: Binary search patience sorting — O(n log n)

def length_of_lis(nums):
    """O(n log n) time, O(n) space — patience sorting"""
    tails = []   # tails[i] = smallest tail of all LIS of length i+1
    for num in nums:
        # Binary search for leftmost tail >= num
        left, right = 0, len(tails)
        while left < right:
            mid = (left + right) // 2
            if tails[mid] < num: left  = mid + 1
            else:                right = mid
        if left == len(tails):
            tails.append(num)    # extend longest LIS
        else:
            tails[left] = num    # replace to keep tails as small as possible
    return len(tails)

print(length_of_lis([10, 9, 2, 5, 3, 7, 101, 18]))  # 4
print(length_of_lis([0, 1, 0, 3, 2, 3]))            # 4


# ── PROBLEM 27: 3SUM ─────────────────────────────────────────
# Find all unique triplets that sum to zero.
# Input: [-1,0,1,2,-1,-4] → [[-1,-1,2],[-1,0,1]]
# No duplicate triplets in result.
#
# Approach: Sort array. Fix first element, use two pointers for the rest.
#   Skip duplicates to avoid repeating triplets. O(n²) time.

def three_sum(nums):
    """O(n²) time, O(n) space for result"""
    nums.sort()
    result = []
    for i in range(len(nums) - 2):
        if i > 0 and nums[i] == nums[i - 1]: continue  # skip duplicate first element
        left, right = i + 1, len(nums) - 1
        while left < right:
            total = nums[i] + nums[left] + nums[right]
            if total == 0:
                result.append([nums[i], nums[left], nums[right]])
                while left < right and nums[left] == nums[left + 1]:   left  += 1
                while left < right and nums[right] == nums[right - 1]: right -= 1
                left += 1; right -= 1
            elif total < 0: left  += 1
            else:           right -= 1
    return result

print(three_sum([-1, 0, 1, 2, -1, -4]))  # [[-1,-1,2],[-1,0,1]]
print(three_sum([0, 0, 0]))              # [[0,0,0]]


# ── PROBLEM 28: TRAPPING RAIN WATER ──────────────────────────
# Given an elevation map, compute how much water can be trapped.
# Input: [0,1,0,2,1,0,1,3,2,1,2,1] → 6
#
# Approach: Two pointers — track max left height and max right height.
#   Water at position i = min(max_left, max_right) - height[i]
#   Move the pointer with the smaller max inward.

def trap_rain_water(height):
    """O(n) time, O(1) space"""
    left, right   = 0, len(height) - 1
    max_left = max_right = 0
    water    = 0
    while left < right:
        if height[left] < height[right]:
            if height[left] >= max_left:
                max_left = height[left]
            else:
                water += max_left - height[left]
            left += 1
        else:
            if height[right] >= max_right:
                max_right = height[right]
            else:
                water += max_right - height[right]
            right -= 1
    return water

print(trap_rain_water([0,1,0,2,1,0,1,3,2,1,2,1]))  # 6
print(trap_rain_water([4,2,0,3,2,5]))               # 9


# ── PROBLEM 29: GROUP ANAGRAMS ────────────────────────────────
# Group strings that are anagrams of each other.
# Input: ["eat","tea","tan","ate","nat","bat"] → [["eat","tea","ate"],["tan","nat"],["bat"]]
#
# Approach: Sort each string → use sorted string as hashmap key.
#   Anagrams will all produce the same sorted key.

def group_anagrams(strs):
    """O(n × L log L) time, O(n) space   — n=number of strings, L=max length"""
    groups = defaultdict(list)
    for s in strs:
        key = tuple(sorted(s))
        groups[key].append(s)
    return list(groups.values())

# Alternative O(n × L): use character count tuple as key
def group_anagrams_count(strs):
    """O(n × L) time using character frequency as key"""
    groups = defaultdict(list)
    for s in strs:
        count = [0] * 26
        for c in s:
            count[ord(c) - ord('a')] += 1
        groups[tuple(count)].append(s)
    return list(groups.values())

print(group_anagrams(["eat","tea","tan","ate","nat","bat"]))
# [["eat","tea","ate"],["tan","nat"],["bat"]]


# ── PROBLEM 30: MIN STACK ─────────────────────────────────────
# Design a stack that supports push, pop, top, and getMin in O(1).
#
# Approach: Maintain a secondary "min stack" that tracks the current minimum.
#   When we push x, push min(x, current_min) onto min_stack.
#   When we pop, pop both stacks simultaneously.

class MinStack:
    """All operations O(1) time"""
    def __init__(self):
        self.stack     = []
        self.min_stack = []   # parallel stack: min_stack[i] = min of stack[0..i]

    def push(self, val):
        self.stack.append(val)
        current_min = min(val, self.min_stack[-1] if self.min_stack else val)
        self.min_stack.append(current_min)

    def pop(self):
        self.stack.pop()
        self.min_stack.pop()

    def top(self):
        return self.stack[-1]

    def get_min(self):
        return self.min_stack[-1]

ms = MinStack()
ms.push(-2); ms.push(0); ms.push(-3)
print(ms.get_min())  # -3
ms.pop()
print(ms.top())      # 0
print(ms.get_min())  # -2


# ── PROBLEM 31: LRU CACHE ─────────────────────────────────────
# Least Recently Used Cache: fixed capacity. On overflow, evict least recently used.
# get(key)      → return value if exists, else -1  (O(1))
# put(key, val) → insert/update; evict LRU if over capacity (O(1))
#
# Approach: Doubly linked list + HashMap.
#   DLL tracks access order (MRU at front, LRU at back).
#   HashMap gives O(1) access to any node for O(1) move-to-front.

class LRUCache:
    """All operations O(1) time, O(capacity) space"""
    class Node:
        def __init__(self, key=0, val=0):
            self.key  = key
            self.val  = val
            self.prev = None
            self.next = None

    def __init__(self, capacity):
        self.capacity = capacity
        self.cache    = {}   # key → Node
        # Sentinel head (MRU side) and tail (LRU side)
        self.head = self.Node()
        self.tail = self.Node()
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev

    def _add_to_front(self, node):
        node.next       = self.head.next
        node.prev       = self.head
        self.head.next.prev = node
        self.head.next  = node

    def get(self, key):
        if key not in self.cache: return -1
        node = self.cache[key]
        self._remove(node)
        self._add_to_front(node)   # mark as most recently used
        return node.val

    def put(self, key, value):
        if key in self.cache:
            self._remove(self.cache[key])
        node = self.Node(key, value)
        self._add_to_front(node)
        self.cache[key] = node
        if len(self.cache) > self.capacity:
            lru = self.tail.prev     # least recently used
            self._remove(lru)
            del self.cache[lru.key]

lru = LRUCache(2)
lru.put(1, 1); lru.put(2, 2)
print(lru.get(1))    # 1
lru.put(3, 3)        # evicts key 2 (LRU)
print(lru.get(2))    # -1 (evicted)
print(lru.get(3))    # 3


# ── PROBLEM 32: LONGEST PALINDROMIC SUBSTRING ────────────────
# Find the longest palindromic substring.
# Input: "babad" → "bab" or "aba"
# Input: "cbbd"  → "bb"
#
# Approach: Expand Around Center — for each position, expand outward.
#   Two cases: odd-length palindromes (single center) and even (double center).
#   O(n²) time, O(1) space — better than O(n³) brute force.

def longest_palindrome_substring(s):
    """O(n²) time, O(1) space"""
    start = end = 0

    def expand(left, right):
        while left >= 0 and right < len(s) and s[left] == s[right]:
            left  -= 1
            right += 1
        return left + 1, right - 1   # last valid palindrome boundaries

    for i in range(len(s)):
        l1, r1 = expand(i, i)       # odd length
        l2, r2 = expand(i, i + 1)   # even length
        if r1 - l1 > end - start: start, end = l1, r1
        if r2 - l2 > end - start: start, end = l2, r2

    return s[start:end + 1]

print(longest_palindrome_substring("babad"))        # "bab"
print(longest_palindrome_substring("cbbd"))         # "bb"
print(longest_palindrome_substring("raceacar"))     # "aca"
