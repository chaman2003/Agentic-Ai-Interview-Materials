// ============================================================
// DSA PROBLEMS — JavaScript Solutions — 30 Interview Problems
// ============================================================
// Format per problem:
//   - Problem statement + examples
//   - Approach explanation
//   - Time / Space complexity
//   - Clean solution + test output


// ── PROBLEM 1: TWO SUM ───────────────────────────────────────
// Given array and target, return indices of two numbers summing to target.
// Input: nums=[2,7,11,15], target=9 → [0,1]
// Approach: HashMap — store value→index; check if complement exists. O(n)

const twoSum = (nums, target) => {
    const map = {};
    for (let i = 0; i < nums.length; i++) {
        const complement = target - nums[i];
        if (map[complement] !== undefined) return [map[complement], i];
        map[nums[i]] = i;
    }
    return [];
};
// Time: O(n) | Space: O(n)
console.log(twoSum([2, 7, 11, 15], 9));  // [0, 1]
console.log(twoSum([3, 2, 4], 6));       // [1, 2]


// ── PROBLEM 2: VALID PARENTHESES ─────────────────────────────
// Return true if all brackets are properly matched and nested.
// Input: "()[]{}" → true  |  "([)]" → false
// Approach: Stack — push openers, match closers against top of stack.

const isValidParentheses = (s) => {
    const stack = [];
    const pairs = { ")": "(", "}": "{", "]": "[" };
    for (const char of s) {
        if ("({[".includes(char)) {
            stack.push(char);
        } else {
            if (!stack.length || stack[stack.length - 1] !== pairs[char]) return false;
            stack.pop();
        }
    }
    return stack.length === 0;
};
// Time: O(n) | Space: O(n)
console.log(isValidParentheses("()[]{}"));  // true
console.log(isValidParentheses("([)]"));    // false
console.log(isValidParentheses("{[]}"));    // true


// ── PROBLEM 3: BEST TIME TO BUY AND SELL STOCK ───────────────
// Find max profit from one buy + one sell (buy before sell).
// Input: [7,1,5,3,6,4] → 5  (buy@1, sell@6)
// Approach: One pass — track min price seen, compute max profit at each step.

const maxProfit = (prices) => {
    let minPrice   = Infinity;
    let bestProfit = 0;
    for (const price of prices) {
        if (price < minPrice)                 minPrice   = price;
        else if (price - minPrice > bestProfit) bestProfit = price - minPrice;
    }
    return bestProfit;
};
// Time: O(n) | Space: O(1)
console.log(maxProfit([7, 1, 5, 3, 6, 4]));  // 5
console.log(maxProfit([7, 6, 4, 3, 1]));      // 0


// ── PROBLEM 4: MAXIMUM SUBARRAY (Kadane's Algorithm) ─────────
// Find contiguous subarray with largest sum.
// Input: [-2,1,-3,4,-1,2,1,-5,4] → 6
// Approach: At each index, either extend subarray or start fresh.

const maxSubarray = (nums) => {
    let maxSum     = nums[0];
    let currentSum = nums[0];
    for (let i = 1; i < nums.length; i++) {
        currentSum = Math.max(nums[i], currentSum + nums[i]);
        maxSum     = Math.max(maxSum, currentSum);
    }
    return maxSum;
};
// Time: O(n) | Space: O(1)
console.log(maxSubarray([-2, 1, -3, 4, -1, 2, 1, -5, 4]));  // 6


// ── PROBLEM 5: CLIMBING STAIRS ────────────────────────────────
// Can climb 1 or 2 steps. How many distinct ways to reach step n?
// Input: n=5 → 8
// Approach: Fibonacci DP — ways(n) = ways(n-1) + ways(n-2).

const climbStairs = (n) => {
    if (n <= 2) return n;
    let prev2 = 1, prev1 = 2;
    for (let i = 3; i <= n; i++) {
        [prev2, prev1] = [prev1, prev1 + prev2];
    }
    return prev1;
};
// Time: O(n) | Space: O(1)
console.log(climbStairs(5));   // 8
console.log(climbStairs(10));  // 89


// ── PROBLEM 6: COIN CHANGE ────────────────────────────────────
// Minimum coins to make amount. Return -1 if impossible.
// Input: coins=[1,5,6,9], amount=11 → 2  (5+6)
// Approach: Bottom-up DP — dp[i] = min coins for amount i.

const coinChange = (coins, amount) => {
    const dp = new Array(amount + 1).fill(Infinity);
    dp[0] = 0;
    for (let i = 1; i <= amount; i++) {
        for (const coin of coins) {
            if (coin <= i) dp[i] = Math.min(dp[i], dp[i - coin] + 1);
        }
    }
    return dp[amount] === Infinity ? -1 : dp[amount];
};
// Time: O(amount × coins.length) | Space: O(amount)
console.log(coinChange([1, 5, 6, 9], 11));  // 2
console.log(coinChange([2], 3));            // -1


// ── PROBLEM 7: LONGEST COMMON SUBSEQUENCE ────────────────────
// Find length of longest subsequence in both strings.
// Input: text1="abcde", text2="ace" → 3
// Approach: 2D DP — dp[i][j] = LCS length for text1[0..i-1] and text2[0..j-1].

const longestCommonSubsequence = (text1, text2) => {
    const m  = text1.length, n = text2.length;
    const dp = Array.from({ length: m + 1 }, () => new Array(n + 1).fill(0));
    for (let i = 1; i <= m; i++) {
        for (let j = 1; j <= n; j++) {
            if (text1[i - 1] === text2[j - 1]) dp[i][j] = dp[i-1][j-1] + 1;
            else                                dp[i][j] = Math.max(dp[i-1][j], dp[i][j-1]);
        }
    }
    return dp[m][n];
};
// Time: O(m×n) | Space: O(m×n)
console.log(longestCommonSubsequence("abcde", "ace"));  // 3
console.log(longestCommonSubsequence("abc", "abc"));    // 3


// ── PROBLEM 8: HOUSE ROBBER ───────────────────────────────────
// Rob non-adjacent houses to maximize total.
// Input: [2,7,9,3,1] → 12  (2+9+1)
// Approach: dp[i] = max(nums[i] + dp[i-2], dp[i-1]). Use 2 vars for O(1) space.

const houseRobber = (nums) => {
    let prev2 = 0, prev1 = 0;
    for (const num of nums) {
        [prev2, prev1] = [prev1, Math.max(prev1, prev2 + num)];
    }
    return prev1;
};
// Time: O(n) | Space: O(1)
console.log(houseRobber([1, 2, 3, 1]));     // 4
console.log(houseRobber([2, 7, 9, 3, 1]));  // 12


// ── PROBLEM 9: NUMBER OF ISLANDS ─────────────────────────────
// Count islands in a 2D grid ('1'=land, '0'=water).
// Approach: DFS flood fill — sink each island when found, count starts.

const numIslands = (grid) => {
    if (!grid.length) return 0;
    const rows = grid.length, cols = grid[0].length;
    let count = 0;

    const dfs = (r, c) => {
        if (r < 0 || r >= rows || c < 0 || c >= cols || grid[r][c] !== "1") return;
        grid[r][c] = "0";  // sink (mark visited)
        dfs(r+1, c); dfs(r-1, c); dfs(r, c+1); dfs(r, c-1);
    };

    for (let r = 0; r < rows; r++) {
        for (let c = 0; c < cols; c++) {
            if (grid[r][c] === "1") { dfs(r, c); count++; }
        }
    }
    return count;
};
// Time: O(m×n) | Space: O(m×n)
console.log(numIslands([["1","1","0"],["0","1","0"],["0","0","1"]]));  // 2


// ── PROBLEM 10: COURSE SCHEDULE ───────────────────────────────
// Can you finish all courses given prerequisites? (cycle detection in DAG)
// Input: n=4, prerequisites=[[1,0],[2,0],[3,1],[3,2]] → true
// Approach: Kahn's topological sort (BFS). If all nodes processed → no cycle.

const canFinish = (numCourses, prerequisites) => {
    const graph    = Array.from({ length: numCourses }, () => []);
    const inDegree = new Array(numCourses).fill(0);

    for (const [course, prereq] of prerequisites) {
        graph[prereq].push(course);
        inDegree[course]++;
    }

    const queue    = [];
    for (let i = 0; i < numCourses; i++) if (inDegree[i] === 0) queue.push(i);
    let finished = 0;

    while (queue.length) {
        const node = queue.shift();
        finished++;
        for (const neighbor of graph[node]) {
            inDegree[neighbor]--;
            if (inDegree[neighbor] === 0) queue.push(neighbor);
        }
    }
    return finished === numCourses;
};
// Time: O(V+E) | Space: O(V+E)
console.log(canFinish(2, [[1, 0]]));           // true
console.log(canFinish(2, [[1, 0], [0, 1]]));   // false


// ── PROBLEM 11: MERGE INTERVALS ───────────────────────────────
// Merge all overlapping intervals.
// Input: [[1,3],[2,6],[8,10],[15,18]] → [[1,6],[8,10],[15,18]]
// Approach: Sort by start. Merge with last interval if overlapping.

const mergeIntervals = (intervals) => {
    intervals.sort((a, b) => a[0] - b[0]);
    const merged = [intervals[0]];
    for (const [start, end] of intervals.slice(1)) {
        if (start <= merged[merged.length - 1][1]) {
            merged[merged.length - 1][1] = Math.max(merged[merged.length - 1][1], end);
        } else {
            merged.push([start, end]);
        }
    }
    return merged;
};
// Time: O(n log n) | Space: O(n)
console.log(JSON.stringify(mergeIntervals([[1,3],[2,6],[8,10],[15,18]])));
// [[1,6],[8,10],[15,18]]


// ── PROBLEM 12: BINARY SEARCH ─────────────────────────────────
// Find target in sorted array. Return index or -1.
// Also: search in rotated sorted array.

const binarySearch = (arr, target) => {
    let left = 0, right = arr.length - 1;
    while (left <= right) {
        const mid = Math.floor((left + right) / 2);
        if (arr[mid] === target)      return mid;
        else if (arr[mid] < target)   left  = mid + 1;
        else                          right = mid - 1;
    }
    return -1;
};

const searchRotated = (nums, target) => {
    let left = 0, right = nums.length - 1;
    while (left <= right) {
        const mid = Math.floor((left + right) / 2);
        if (nums[mid] === target) return mid;
        if (nums[left] <= nums[mid]) {   // left half sorted
            if (nums[left] <= target && target < nums[mid]) right = mid - 1;
            else                                             left  = mid + 1;
        } else {                         // right half sorted
            if (nums[mid] < target && target <= nums[right]) left  = mid + 1;
            else                                              right = mid - 1;
        }
    }
    return -1;
};
// Time: O(log n) | Space: O(1)
console.log(binarySearch([1, 3, 5, 7, 9], 7));        // 3
console.log(searchRotated([4, 5, 6, 7, 0, 1, 2], 0)); // 4


// ── PROBLEM 13: MERGE SORT ────────────────────────────────────
// Divide-and-conquer sort. Stable. O(n log n) all cases.

const mergeSort = (arr) => {
    if (arr.length <= 1) return arr;
    const mid   = Math.floor(arr.length / 2);
    const left  = mergeSort(arr.slice(0, mid));
    const right = mergeSort(arr.slice(mid));
    return merge(left, right);
};

const merge = (left, right) => {
    const result = [];
    let i = 0, j = 0;
    while (i < left.length && j < right.length) {
        if (left[i] <= right[j]) result.push(left[i++]);
        else                     result.push(right[j++]);
    }
    return result.concat(left.slice(i)).concat(right.slice(j));
};
// Time: O(n log n) | Space: O(n)
console.log(mergeSort([38, 27, 43, 3, 9, 82, 10]));  // [3,9,10,27,38,43,82]


// ── PROBLEM 14: QUICK SORT ────────────────────────────────────
// Divide-and-conquer. Pick pivot, partition, recurse on both sides.
// In-place. O(n log n) average, O(n²) worst.

const quickSort = (arr, low = 0, high = arr.length - 1) => {
    if (low < high) {
        const pivot = partition(arr, low, high);
        quickSort(arr, low, pivot - 1);
        quickSort(arr, pivot + 1, high);
    }
    return arr;
};

const partition = (arr, low, high) => {
    const pivot = arr[high];
    let store   = low;
    for (let j = low; j < high; j++) {
        if (arr[j] <= pivot) {
            [arr[store], arr[j]] = [arr[j], arr[store]];
            store++;
        }
    }
    [arr[store], arr[high]] = [arr[high], arr[store]];
    return store;
};
// Time: O(n log n) avg | Space: O(log n) stack
console.log(quickSort([10, 7, 8, 9, 1, 5]));  // [1,5,7,8,9,10]


// ── PROBLEM 15: REVERSE LINKED LIST ──────────────────────────
// Reverse a singly linked list.
// Input: 1→2→3→4→5  →  5→4→3→2→1

class ListNode {
    constructor(val = 0, next = null) { this.val = val; this.next = next; }
}

const reverseList = (head) => {
    let prev = null, curr = head;
    while (curr) {
        const next = curr.next;
        curr.next  = prev;
        prev       = curr;
        curr       = next;
    }
    return prev;
};

const reverseListRecursive = (head, prev = null) => {
    if (!head) return prev;
    const next = head.next;
    head.next  = prev;
    return reverseListRecursive(next, head);
};
// Time: O(n) | Space: O(1) iterative, O(n) recursive

const buildList = (...vals) => {
    if (!vals.length) return null;
    const head = new ListNode(vals[0]);
    let curr = head;
    for (let i = 1; i < vals.length; i++) { curr.next = new ListNode(vals[i]); curr = curr.next; }
    return head;
};
const listToArray = (head) => { const r = []; while (head) { r.push(head.val); head = head.next; } return r; };

console.log(listToArray(reverseList(buildList(1,2,3,4,5))));           // [5,4,3,2,1]
console.log(listToArray(reverseListRecursive(buildList(1,2,3,4,5))));  // [5,4,3,2,1]


// ── PROBLEM 16: DETECT CYCLE IN LINKED LIST ──────────────────
// Return true if linked list has a cycle.
// Approach: Floyd's fast/slow pointers — if they meet, cycle exists.

const hasCycle = (head) => {
    let slow = head, fast = head;
    while (fast && fast.next) {
        slow = slow.next;
        fast = fast.next.next;
        if (slow === fast) return true;
    }
    return false;
};
// Time: O(n) | Space: O(1)

const n1 = new ListNode(1), n2 = new ListNode(2), n3 = new ListNode(3);
n1.next = n2; n2.next = n3; n3.next = n2;  // cycle: 3 → 2
console.log(hasCycle(n1));                  // true
console.log(hasCycle(buildList(1,2,3)));    // false


// ── PROBLEM 17: FIND KTH LARGEST ELEMENT ─────────────────────
// Find the kth largest element (1-indexed, not distinct).
// Input: nums=[3,2,1,5,6,4], k=2 → 5
// Approach: Min-heap of size k — heap top = kth largest.

class MinHeap {
    constructor() { this.heap = []; }
    push(val) {
        this.heap.push(val);
        let i = this.heap.length - 1;
        while (i > 0) {
            const parent = Math.floor((i - 1) / 2);
            if (this.heap[parent] > this.heap[i]) {
                [this.heap[parent], this.heap[i]] = [this.heap[i], this.heap[parent]];
                i = parent;
            } else break;
        }
    }
    pop() {
        const top = this.heap[0];
        const last = this.heap.pop();
        if (this.heap.length) {
            this.heap[0] = last;
            let i = 0;
            while (true) {
                let min = i, l = 2*i+1, r = 2*i+2;
                if (l < this.heap.length && this.heap[l] < this.heap[min]) min = l;
                if (r < this.heap.length && this.heap[r] < this.heap[min]) min = r;
                if (min === i) break;
                [this.heap[i], this.heap[min]] = [this.heap[min], this.heap[i]];
                i = min;
            }
        }
        return top;
    }
    peek() { return this.heap[0]; }
    size() { return this.heap.length; }
}

const findKthLargest = (nums, k) => {
    const heap = new MinHeap();
    for (const num of nums) {
        heap.push(num);
        if (heap.size() > k) heap.pop();
    }
    return heap.peek();
};
// Time: O(n log k) | Space: O(k)
console.log(findKthLargest([3, 2, 1, 5, 6, 4], 2));  // 5
console.log(findKthLargest([3, 2, 3, 1, 2, 4, 5, 5, 6], 4));  // 4


// ── PROBLEM 18: VALIDATE BST ─────────────────────────────────
// Determine if a binary tree is a valid BST.
// Approach: Pass valid range [minVal, maxVal] to each node recursively.

class TreeNode {
    constructor(val = 0, left = null, right = null) {
        this.val = val; this.left = left; this.right = right;
    }
}

const isValidBST = (root, minVal = -Infinity, maxVal = Infinity) => {
    if (!root) return true;
    if (root.val <= minVal || root.val >= maxVal) return false;
    return isValidBST(root.left, minVal, root.val) &&
           isValidBST(root.right, root.val, maxVal);
};
// Time: O(n) | Space: O(h)
const validBST   = new TreeNode(2, new TreeNode(1), new TreeNode(3));
const invalidBST = new TreeNode(5, new TreeNode(1), new TreeNode(4, new TreeNode(3), new TreeNode(6)));
console.log(isValidBST(validBST));    // true
console.log(isValidBST(invalidBST));  // false


// ── PROBLEM 19: MAX DEPTH OF BINARY TREE ─────────────────────
// Return maximum depth (height) of a binary tree.

const maxDepth = (root) => {
    if (!root) return 0;
    return 1 + Math.max(maxDepth(root.left), maxDepth(root.right));
};
// Time: O(n) | Space: O(h)
const tree = new TreeNode(3, new TreeNode(9), new TreeNode(20, new TreeNode(15), new TreeNode(7)));
console.log(maxDepth(tree));  // 3


// ── PROBLEM 20: INORDER TRAVERSAL ────────────────────────────
// Return inorder (Left→Root→Right) traversal.
// For BST: produces sorted order.

const inorderTraversal = (root) => {
    const result = [], stack = [];
    let curr = root;
    while (curr || stack.length) {
        while (curr) { stack.push(curr); curr = curr.left; }
        curr = stack.pop();
        result.push(curr.val);
        curr = curr.right;
    }
    return result;
};
// Time: O(n) | Space: O(h)
const bst = new TreeNode(4, new TreeNode(2, new TreeNode(1), new TreeNode(3)),
                            new TreeNode(6, new TreeNode(5), new TreeNode(7)));
console.log(inorderTraversal(bst));  // [1,2,3,4,5,6,7]


// ── PROBLEM 21: LCA OF BST ───────────────────────────────────
// Lowest Common Ancestor of two nodes in a BST.
// Input: root=6, p=2, q=8 → 6

const lcaBST = (root, p, q) => {
    while (root) {
        if (p.val < root.val && q.val < root.val)      root = root.left;
        else if (p.val > root.val && q.val > root.val)  root = root.right;
        else                                             return root;
    }
    return null;
};
// Time: O(log n) avg | Space: O(1)
const rootBST = new TreeNode(6,
    new TreeNode(2, new TreeNode(0), new TreeNode(4)),
    new TreeNode(8, new TreeNode(7), new TreeNode(9)));
console.log(lcaBST(rootBST, rootBST.left, rootBST.right).val);  // 6
console.log(lcaBST(rootBST, rootBST.left, rootBST.left.right).val);  // 2


// ── PROBLEM 22: SERIALIZE AND DESERIALIZE BINARY TREE ────────
// Encode tree to string, decode string back to tree.
// Approach: BFS level-order with "X" for nulls.

const serialize = (root) => {
    if (!root) return "X";
    const queue  = [root], result = [];
    while (queue.length) {
        const node = queue.shift();
        if (node) {
            result.push(String(node.val));
            queue.push(node.left); queue.push(node.right);
        } else {
            result.push("X");
        }
    }
    return result.join(",");
};

const deserialize = (data) => {
    if (data === "X") return null;
    const vals  = data.split(",");
    const root  = new TreeNode(parseInt(vals[0]));
    const queue = [root];
    let i = 1;
    while (queue.length && i < vals.length) {
        const node = queue.shift();
        if (vals[i] !== "X") { node.left  = new TreeNode(parseInt(vals[i])); queue.push(node.left);  }
        i++;
        if (i < vals.length && vals[i] !== "X") {
            node.right = new TreeNode(parseInt(vals[i])); queue.push(node.right);
        }
        i++;
    }
    return root;
};
// Time: O(n) | Space: O(n)
const treeForSer  = new TreeNode(1, new TreeNode(2), new TreeNode(3, new TreeNode(4), new TreeNode(5)));
const encoded     = serialize(treeForSer);
const decoded     = deserialize(encoded);
console.log(encoded);                        // "1,2,3,X,X,4,5"
console.log(inorderTraversal(decoded));      // [2,1,4,3,5]


// ── PROBLEM 23: SPIRAL MATRIX ─────────────────────────────────
// Return all elements in spiral order (layer by layer, clockwise).
// Input: [[1,2,3],[4,5,6],[7,8,9]] → [1,2,3,6,9,8,7,4,5]

const spiralOrder = (matrix) => {
    const result = [];
    let top = 0, bottom = matrix.length - 1;
    let left = 0, right = matrix[0].length - 1;

    while (top <= bottom && left <= right) {
        for (let c = left; c <= right; c++)   result.push(matrix[top][c]);    top++;
        for (let r = top; r <= bottom; r++)   result.push(matrix[r][right]);  right--;
        if (top <= bottom) { for (let c = right; c >= left; c--) result.push(matrix[bottom][c]); bottom--; }
        if (left <= right) { for (let r = bottom; r >= top; r--) result.push(matrix[r][left]);   left++;   }
    }
    return result;
};
// Time: O(m×n) | Space: O(m×n)
console.log(spiralOrder([[1,2,3],[4,5,6],[7,8,9]]));  // [1,2,3,6,9,8,7,4,5]


// ── PROBLEM 24: WORD SEARCH ───────────────────────────────────
// Find if a word exists in a 2D grid (adjacent cells, no cell reuse).
// Approach: DFS backtracking from each starting cell.

const wordSearch = (board, word) => {
    const rows = board.length, cols = board[0].length;

    const dfs = (r, c, idx) => {
        if (idx === word.length) return true;
        if (r < 0 || r >= rows || c < 0 || c >= cols || board[r][c] !== word[idx]) return false;
        const temp  = board[r][c];
        board[r][c] = "#";  // mark visited
        const found = dfs(r+1,c,idx+1) || dfs(r-1,c,idx+1) || dfs(r,c+1,idx+1) || dfs(r,c-1,idx+1);
        board[r][c] = temp; // restore (backtrack)
        return found;
    };

    for (let r = 0; r < rows; r++)
        for (let c = 0; c < cols; c++)
            if (dfs(r, c, 0)) return true;
    return false;
};
// Time: O(m×n×4^L) | Space: O(L) recursion
const boardWS = [["A","B","C","E"],["S","F","C","S"],["A","D","E","E"]];
console.log(wordSearch(boardWS, "ABCCED"));  // true
console.log(wordSearch(boardWS, "ABCB"));    // false


// ── PROBLEM 25: THREE SUM ─────────────────────────────────────
// Find all unique triplets that sum to zero.
// Input: [-1,0,1,2,-1,-4] → [[-1,-1,2],[-1,0,1]]
// Approach: Sort + fix first element + two pointers.

const threeSum = (nums) => {
    nums.sort((a, b) => a - b);
    const result = [];
    for (let i = 0; i < nums.length - 2; i++) {
        if (i > 0 && nums[i] === nums[i-1]) continue;  // skip duplicate first
        let left = i + 1, right = nums.length - 1;
        while (left < right) {
            const total = nums[i] + nums[left] + nums[right];
            if (total === 0) {
                result.push([nums[i], nums[left], nums[right]]);
                while (left < right && nums[left]  === nums[left+1])  left++;
                while (left < right && nums[right] === nums[right-1]) right--;
                left++; right--;
            } else if (total < 0) left++;
            else                  right--;
        }
    }
    return result;
};
// Time: O(n²) | Space: O(n) result
console.log(JSON.stringify(threeSum([-1, 0, 1, 2, -1, -4])));  // [[-1,-1,2],[-1,0,1]]


// ── PROBLEM 26: TRAPPING RAIN WATER ──────────────────────────
// Compute trapped water given elevation map.
// Input: [0,1,0,2,1,0,1,3,2,1,2,1] → 6
// Approach: Two pointers — water = min(maxL, maxR) - height[i].

const trapRainWater = (height) => {
    let left = 0, right = height.length - 1;
    let maxLeft = 0, maxRight = 0, water = 0;
    while (left < right) {
        if (height[left] < height[right]) {
            if (height[left] >= maxLeft) maxLeft = height[left];
            else                         water   += maxLeft - height[left];
            left++;
        } else {
            if (height[right] >= maxRight) maxRight = height[right];
            else                           water    += maxRight - height[right];
            right--;
        }
    }
    return water;
};
// Time: O(n) | Space: O(1)
console.log(trapRainWater([0,1,0,2,1,0,1,3,2,1,2,1]));  // 6
console.log(trapRainWater([4,2,0,3,2,5]));               // 9


// ── PROBLEM 27: GROUP ANAGRAMS ────────────────────────────────
// Group strings that are anagrams of each other.
// Input: ["eat","tea","tan","ate","nat","bat"]

const groupAnagrams = (strs) => {
    const map = new Map();
    for (const s of strs) {
        const key = [...s].sort().join("");
        if (!map.has(key)) map.set(key, []);
        map.get(key).push(s);
    }
    return [...map.values()];
};
// Time: O(n × L log L) | Space: O(n)
console.log(groupAnagrams(["eat","tea","tan","ate","nat","bat"]));
// [["eat","tea","ate"],["tan","nat"],["bat"]]


// ── PROBLEM 28: MIN STACK ─────────────────────────────────────
// Stack with O(1) push, pop, top, getMin.
// Approach: Parallel min_stack tracking current min at each state.

class MinStack {
    constructor() { this.stack = []; this.minStack = []; }
    push(val) {
        this.stack.push(val);
        const min = !this.minStack.length ? val : Math.min(val, this.minStack[this.minStack.length-1]);
        this.minStack.push(min);
    }
    pop()    { this.stack.pop(); this.minStack.pop(); }
    top()    { return this.stack[this.stack.length - 1]; }
    getMin() { return this.minStack[this.minStack.length - 1]; }
}
// All operations O(1)
const ms = new MinStack();
ms.push(-2); ms.push(0); ms.push(-3);
console.log(ms.getMin());  // -3
ms.pop();
console.log(ms.top());     // 0
console.log(ms.getMin());  // -2


// ── PROBLEM 29: LRU CACHE ─────────────────────────────────────
// Least Recently Used cache. O(1) get and put.
// Approach: Doubly linked list (order) + Map (O(1) access).

class LRUCache {
    constructor(capacity) {
        this.capacity = capacity;
        this.map      = new Map();   // Map preserves insertion order
    }
    get(key) {
        if (!this.map.has(key)) return -1;
        const val = this.map.get(key);
        this.map.delete(key);
        this.map.set(key, val);      // re-insert = most recently used
        return val;
    }
    put(key, value) {
        if (this.map.has(key)) this.map.delete(key);
        this.map.set(key, value);
        if (this.map.size > this.capacity) {
            this.map.delete(this.map.keys().next().value);  // delete oldest (LRU)
        }
    }
}
// Time: O(1) | Space: O(capacity)
// Note: JS Map preserves insertion order, making LRU elegant.
const lru = new LRUCache(2);
lru.put(1, 1); lru.put(2, 2);
console.log(lru.get(1));   // 1
lru.put(3, 3);             // evicts key 2
console.log(lru.get(2));   // -1


// ── PROBLEM 30: LONGEST PALINDROMIC SUBSTRING ────────────────
// Find the longest palindromic substring.
// Input: "babad" → "bab"  |  "cbbd" → "bb"
// Approach: Expand around center — O(n²), O(1) space.

const longestPalindrome = (s) => {
    let start = 0, end = 0;

    const expand = (l, r) => {
        while (l >= 0 && r < s.length && s[l] === s[r]) { l--; r++; }
        return [l + 1, r - 1];
    };

    for (let i = 0; i < s.length; i++) {
        const [l1, r1] = expand(i, i);      // odd length
        const [l2, r2] = expand(i, i + 1);  // even length
        if (r1 - l1 > end - start) [start, end] = [l1, r1];
        if (r2 - l2 > end - start) [start, end] = [l2, r2];
    }
    return s.slice(start, end + 1);
};
// Time: O(n²) | Space: O(1)
console.log(longestPalindrome("babad"));    // "bab"
console.log(longestPalindrome("cbbd"));     // "bb"
console.log(longestPalindrome("racecar"));  // "racecar"


// ── COMPLEXITY CHEAT SHEET ────────────────────────────────────
/*
Data Structure      | Access | Search | Insert | Delete | Space
--------------------|--------|--------|--------|--------|------
Array               | O(1)   | O(n)   | O(n)   | O(n)   | O(n)
Linked List         | O(n)   | O(n)   | O(1)*  | O(1)*  | O(n)
HashMap / Set       | -      | O(1)†  | O(1)†  | O(1)†  | O(n)
Binary Heap         | O(1)** | O(n)   | O(logn)| O(logn)| O(n)
Binary Search Tree  | O(logn)†|O(logn)†|O(logn)†|O(logn)†| O(n)

  * = at head/tail with pointer    ** = only min/max
  † = average case

Algorithm          | Best     | Average  | Worst    | Space
-------------------|----------|----------|----------|--------
Binary Search      | O(1)     | O(log n) | O(log n) | O(1)
Merge Sort         | O(nlogn) | O(nlogn) | O(nlogn) | O(n)
Quick Sort         | O(nlogn) | O(nlogn) | O(n²)    | O(logn)
Bubble Sort        | O(n)     | O(n²)    | O(n²)    | O(1)
BFS / DFS          | O(V+E)   | O(V+E)   | O(V+E)   | O(V)
Dijkstra           | -        | O((V+E)logV) | -    | O(V)
*/
