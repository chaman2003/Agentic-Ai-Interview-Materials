# React — Advanced Q&A, Performance & Patterns

---

## RECONCILIATION AND RENDERING

**Q: How does React's reconciliation algorithm work?**
A: When state changes, React creates a new Virtual DOM tree and diffs it against the previous one. Rules:
1. Elements with different types → unmount old, mount new (full remount)
2. Same type elements → update attributes/props in place
3. Lists require a unique `key` prop to efficiently track which items changed

**Q: What is the `key` prop and why does it matter?**
A: `key` tells React which list item is which across renders. Without a stable key, React can't tell if an item moved, was added, or was deleted — it remounts everything unnecessarily (or worse, mixes up state).
```jsx
// BAD — using index as key when list can be reordered/filtered
{users.map((user, i) => <UserCard key={i} user={user} />)}

// GOOD — use stable unique ID
{users.map(user => <UserCard key={user.id} user={user} />)}
```

---

**Q: What triggers a re-render in React?**
A:
1. `setState` called (or `dispatch` for useReducer)
2. Parent re-renders (passes new props even if same value)
3. Context value changes
4. `forceUpdate()` (class components, avoid)

Not re-render triggers: `useRef` changes, external variables changing.

---

## PERFORMANCE OPTIMIZATION

**Q: When should you use React.memo?**
A: Wrap a component with `React.memo` when:
1. The component renders often with the same props
2. The component is expensive to render
3. The parent re-renders frequently but the child's props don't change

```jsx
// Without memo: re-renders every time parent re-renders
function ExpensiveList({ items }) {
    return <ul>{items.map(i => <li key={i.id}>{i.name}</li>)}</ul>;
}

// With memo: only re-renders when items actually changes
const ExpensiveList = React.memo(function({ items }) {
    return <ul>{items.map(i => <li key={i.id}>{i.name}</li>)}</ul>;
});
```

**Q: What is the difference between React.memo, useMemo, and useCallback?**

| Tool | What it caches | Use when |
|------|--------------|----------|
| `React.memo` | A whole **component**'s output | Prevent child re-render with same props |
| `useMemo` | A **computed value** | Expensive calculation you don't want to redo |
| `useCallback` | A **function reference** | Prevent new function reference on every render (esp. to pass to memo'd child) |

---

**Q: What is the stale closure problem?**
A: A useEffect or callback captures a value at creation time. If the value changes but the closure isn't updated, it uses a stale (old) value.
```jsx
function Timer() {
    const [count, setCount] = useState(0);

    useEffect(() => {
        const id = setInterval(() => {
            console.log(count);   // STALE! Always logs 0 (captured at mount)
            setCount(count + 1);  // STALE! Always sets to 1
        }, 1000);
        return () => clearInterval(id);
    }, []);   // empty deps → only runs once → closes over initial count=0

    // Fix 1: add count to dependencies (but re-creates interval every second)
    // Fix 2: use functional update — doesn't need to close over count
    useEffect(() => {
        const id = setInterval(() => {
            setCount(c => c + 1);   // functional update ← doesn't close over count
        }, 1000);
        return () => clearInterval(id);
    }, []);
}
```

---

## HOOKS DEEP DIVE

**Q: What is the `useLayoutEffect` hook and when do you use it?**
A: Same as `useEffect` but fires BEFORE the browser paints. Use when you need to read/write layout (DOM dimensions, positions) to avoid visual flicker.
```jsx
// useEffect: fires after paint → can cause visible flicker
// useLayoutEffect: fires before paint → seamless

useLayoutEffect(() => {
    const width = ref.current.offsetWidth;
    setWidth(width);   // update state before paint → no flicker
}, []);
```

---

**Q: Write a custom hook that fetches data.**
```jsx
function useFetch(url) {
    const [data, setData]       = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError]     = useState(null);

    useEffect(() => {
        let cancelled = false;
        setLoading(true);

        fetch(url)
            .then(r => {
                if (!r.ok) throw new Error(`HTTP ${r.status}`);
                return r.json();
            })
            .then(data => { if (!cancelled) { setData(data); setLoading(false); } })
            .catch(err => { if (!cancelled) { setError(err.message); setLoading(false); } });

        return () => { cancelled = true; };
    }, [url]);

    return { data, loading, error };
}

// Usage
function UserProfile({ id }) {
    const { data: user, loading, error } = useFetch(`/api/users/${id}`);
    if (loading) return <p>Loading...</p>;
    if (error)   return <p>Error: {error}</p>;
    return <h1>{user.name}</h1>;
}
```

---

**Q: Write a custom hook for local storage.**
```jsx
function useLocalStorage(key, initialValue) {
    const [storedValue, setStoredValue] = useState(() => {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : initialValue;
        } catch {
            return initialValue;
        }
    });

    const setValue = (value) => {
        try {
            setStoredValue(value);
            localStorage.setItem(key, JSON.stringify(value));
        } catch (err) {
            console.error(err);
        }
    };

    return [storedValue, setValue];
}

// Usage — works exactly like useState but persists to localStorage
const [theme, setTheme] = useLocalStorage("theme", "light");
```

---

## CONTEXT ADVANCED

**Q: How do you prevent unnecessary re-renders with Context?**
A: Any component consuming a context re-renders when context value changes. Optimization strategies:
1. Split context into smaller pieces (AuthContext, ThemeContext separately)
2. `useMemo` to stabilize the context value
3. Use Zustand or Redux for complex global state instead of Context

```jsx
// BAD — object created new on every render → all consumers re-render every time
function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    return (
        <AuthContext.Provider value={{ user, setUser }}>   {/* new object every render! */}
            {children}
        </AuthContext.Provider>
    );
}

// GOOD — useMemo stabilizes the value
function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const value = useMemo(() => ({ user, setUser }), [user]);  // only new object when user changes
    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
```

---

## STATE MANAGEMENT COMPARISON

**Q: When to use useState vs useReducer vs Context vs Redux vs Zustand?**

| Scenario | Tool |
|----------|------|
| Simple local state (toggle, form input) | `useState` |
| Complex local state (multiple related values, many actions) | `useReducer` |
| Share state between a few components | `useContext` |
| Large app, many consumers, developer tools needed | Redux Toolkit |
| Medium app, simple API, no boilerplate | Zustand |

---

## COMMON REACT INTERVIEW TRAPS

**Q: Why shouldn't you set state directly in the render?**
```jsx
// INFINITE LOOP ← triggers render → sets state → triggers render...
function Bad() {
    const [x, setX] = useState(0);
    setX(x + 1);   // ← called during render!
    return <div>{x}</div>;
}
// Fix: move to useEffect or event handler
```

**Q: What is batching in React?**
A: React 18 batches multiple state updates in the same event handler into a single re-render (even in async code, setTimeout, etc.). Before React 18, batching only happened in React event handlers.
```jsx
handleClick() {
    setCount(c => c + 1);
    setName("Alice");
    // React batches these → only ONE re-render (not two)
}
```

**Q: What is Suspense?**
A: A component that shows a fallback UI while waiting for async operations (lazy loading, data fetching with libraries that support Suspense).
```jsx
const LazyPage = React.lazy(() => import("./MyPage"));
<Suspense fallback={<Spinner />}>
    <LazyPage />
</Suspense>
```
