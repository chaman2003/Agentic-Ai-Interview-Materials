# React Q&A — Interview Ready (Comprehensive)

---

## CORE FUNDAMENTALS

**Q: What is React?**
A: A JavaScript library for building UIs. You build reusable components. React efficiently updates the real DOM by comparing a virtual DOM diff (reconciliation). Maintained by Meta.

**Q: What is JSX?**
A: HTML-like syntax inside JavaScript. `className` instead of `class`, `onClick` instead of `onclick`. Transpiles to `React.createElement()` calls. Babel or SWC handles this at build time.

**Q: What is the difference between props and state?**
A:
- **Props** — data passed FROM parent TO child. Read-only in the child. Like function arguments.
- **State** — data owned by a component. When it changes, the component re-renders.

**Q: Explain useState.**
A: `const [value, setValue] = useState(initialValue)`. `setValue(newValue)` schedules a re-render. NEVER mutate state directly — always use the setter. For updates based on current state, use functional form: `setValue(prev => prev + 1)`.

**Q: Explain useEffect and its dependency array.**
A: Runs side effects after rendering. The dependency array controls when it runs:
- `[]` — run ONCE when the component mounts
- `[id]` — run every time `id` changes
- no array — run after EVERY render

Always return a cleanup function if you set up subscriptions, timers, or event listeners.

**Q: What is the cleanup function in useEffect?**
A: The function you return from useEffect. Runs when the component unmounts OR before the next effect runs. Used to cancel API calls (AbortController), remove event listeners, clear timers.

**Q: What is useRef?**
A: Two uses:
1. Reference a DOM element directly (`inputRef.current.focus()`)
2. Store a mutable value across renders WITHOUT triggering a re-render (like an instance variable in a class)

**Q: What is useContext?**
A: Share data across the component tree without prop drilling. Create context → provide high up → consume anywhere with `useContext()`.

**Q: What is useMemo?**
A: Caches an expensive computed VALUE. Only recalculates when dependencies change.
```js
const result = useMemo(() => expensiveCalc(data), [data]);
```

**Q: What is useCallback?**
A: Caches a FUNCTION reference. Prevents child components from re-rendering unnecessarily when you pass callbacks as props.
```js
const handler = useCallback(() => doSomething(id), [id]);
```

**Q: useMemo vs useCallback?**
A: `useMemo` → caches a value. `useCallback` → caches a function. `useCallback(fn, deps)` is equivalent to `useMemo(() => fn, deps)`.

**Q: What is React.memo?**
A: Wraps a component to prevent re-renders when props haven't changed (shallow comparison). Use with `useCallback` for callbacks passed as props.

**Q: What is prop drilling and how do you avoid it?**
A: Passing props through many intermediate components just to reach a deeply nested component. Avoid with `useContext` (simple) or Redux/Zustand (complex global state).

**Q: What is useReducer?**
A: Alternative to useState for complex state. Takes a reducer function `(state, action) => newState`. Dispatch actions to update state. Similar to Redux pattern. Use when state has multiple sub-values or when next state depends on the previous.

**Q: What is the virtual DOM?**
A: A lightweight JavaScript copy of the real DOM. When state changes, React builds a new virtual DOM, diffs it against the old one (reconciliation), and only updates the parts of the real DOM that changed (commit phase).

**Q: What is reconciliation in React?**
A: The process React uses to compare the previous virtual DOM tree with the new one and compute the minimal set of real DOM changes. React's Fiber architecture enables this to be incremental and prioritized.

**Q: What is the key prop?**
A: A unique identifier for elements in a list. Helps React identify which items changed, were added, or removed. Never use array index as key if the list can be reordered.

---

## REACT ROUTER v6

**Q: What are React Router v6's core components?**
A:
- `BrowserRouter` — wraps the app, provides routing context
- `Routes` — container that picks the best matching route
- `Route path element` — maps a URL pattern to a component
- `Link to` — navigation without page reload
- `NavLink` — Link with active styling support
- `Navigate to` — declarative redirect
- `Outlet` — renders matched child route inside a parent layout

**Q: What changed from React Router v5 to v6?**
A:
- `Switch` → `Routes` (smarter matching, no need for `exact`)
- `component={Comp}` → `element={<Comp />}` (JSX, not component reference)
- Nested routes are declared together, not across separate files
- `useHistory` → `useNavigate`
- Relative paths work inside nested `Routes`
- `<Outlet />` replaces `{children}` for nested layouts

**Q: How do nested routes work in v6?**
A: Parent route renders `<Outlet />` where child content appears. Child routes are defined as nested `<Route>` elements inside the parent `<Route>`. The `index` attribute marks the default child.
```jsx
<Route path="/dashboard" element={<DashboardLayout />}>
  <Route index element={<Overview />} />
  <Route path="settings" element={<Settings />} />
</Route>
```

**Q: What is useNavigate?**
A: Hook for programmatic navigation. Returns a navigate function.
```js
const navigate = useNavigate()
navigate('/dashboard')          // go to route
navigate(-1)                    // go back
navigate('/login', { replace: true })   // replace history entry
navigate('/page', { state: { from: '/home' } })  // pass state
```

**Q: What is useParams?**
A: Extracts URL path parameters from routes like `/blog/:category/:postId`.
```js
const { category, postId } = useParams()
// URL /blog/tech/42 => { category: 'tech', postId: '42' }
```

**Q: What is useSearchParams?**
A: Reads and writes URL query string parameters.
```js
const [searchParams, setSearchParams] = useSearchParams()
const page = searchParams.get('page') || 1
setSearchParams({ search: 'react', page: 2 })  // updates URL
```

**Q: How do you implement protected routes?**
A: Create a wrapper component that checks auth state and redirects if not authenticated:
```jsx
function ProtectedRoute({ children }) {
  const { user } = useAuth()
  const location = useLocation()
  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }
  return children
}
// Usage:
<Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
```

**Q: What is useLocation?**
A: Returns the current location object: `{ pathname, search, hash, state }`. Useful for reading state passed via `navigate('/path', { state: { ... } })`.

**Q: How does NavLink differ from Link?**
A: `NavLink` receives an `isActive` boolean in its style/className callback, allowing you to style the active link differently:
```jsx
<NavLink to="/home" style={({ isActive }) => ({ fontWeight: isActive ? 'bold' : 'normal' })}>
  Home
</NavLink>
```

---

## SUSPENSE AND CODE SPLITTING

**Q: What is React.lazy?**
A: Creates a lazy-loaded component. The import only runs when the component is first rendered, creating a separate bundle chunk (code splitting).
```js
const Dashboard = lazy(() => import('./Dashboard'))
```

**Q: What is Suspense?**
A: A component that shows a fallback UI while its lazy children are loading. Required when using `React.lazy`.
```jsx
<Suspense fallback={<Spinner />}>
  <LazyDashboard />
</Suspense>
```

**Q: Where should you place Suspense boundaries?**
A: As close as possible to the lazy component for the best UX. You can have multiple Suspense boundaries at different levels — each one shows its own fallback independently.

**Q: What is an Error Boundary?**
A: A class component that catches JavaScript errors in its child tree during rendering, lifecycle methods, and constructors. Must implement `getDerivedStateFromError` to display a fallback UI.
```jsx
class ErrorBoundary extends Component {
  state = { hasError: false }
  static getDerivedStateFromError(error) { return { hasError: true } }
  componentDidCatch(error, info) { logToService(error, info) }
  render() {
    return this.state.hasError ? <Fallback /> : this.props.children
  }
}
```

**Q: Should you combine ErrorBoundary with Suspense?**
A: Yes! Wrap `<Suspense>` with `<ErrorBoundary>` to handle both loading states and network errors:
```jsx
<ErrorBoundary fallback={<p>Failed to load</p>}>
  <Suspense fallback={<Spinner />}>
    <LazyComponent />
  </Suspense>
</ErrorBoundary>
```

**Q: What is code splitting and why does it matter?**
A: Breaking the JavaScript bundle into smaller chunks that are loaded on demand. Reduces initial load time — users only download code for the routes they visit.

---

## REACT 18 CONCURRENT FEATURES

**Q: What is Concurrent Mode / Concurrent React?**
A: React 18's ability to prepare multiple versions of the UI simultaneously and interrupt rendering to handle urgent updates. Enabled by default with `createRoot`. Key benefit: the UI stays responsive even during expensive renders.

**Q: What is useTransition?**
A: Hook that marks state updates as non-urgent (low priority). Urgent updates (like typing) can interrupt the transition.
```js
const [isPending, startTransition] = useTransition()

function handleInput(value) {
  setInputValue(value)          // urgent: update input immediately
  startTransition(() => {
    setSearchResults(search(value)) // non-urgent: can be interrupted
  })
}
```
`isPending` is `true` while the transition is in progress.

**Q: What is useDeferredValue?**
A: Defers the propagation of a value to child components. The child renders with the old value first (keeping UI responsive), then re-renders with the new value when React is idle.
```js
const deferredQuery = useDeferredValue(query)
// Wrap the slow component in React.memo so it only re-renders when deferredQuery changes
<SlowList query={deferredQuery} />
```

**Q: useTransition vs useDeferredValue — when to use which?**
A:
- `useTransition` — when you own the state update (wrap `setState` in `startTransition`)
- `useDeferredValue` — when you receive a value as a prop and want to defer its use in children
- Both mark updates as low-priority; `useTransition` is more explicit about what causes slowness

**Q: What is the difference between `startTransition` standalone and `useTransition`?**
A: `startTransition` is the standalone API (no hook). `useTransition` gives you both `startTransition` and the `isPending` boolean to show loading state during the transition.

**Q: What is React 18's automatic batching?**
A: React 18 batches multiple state updates from any context (timeouts, promises, native events) into a single re-render. Before React 18, batching only happened inside React event handlers.
```js
// Before React 18: two re-renders
// After React 18: one re-render (automatic batching)
setTimeout(() => {
  setCount(c => c + 1)
  setFlag(f => !f)
}, 1000)
```

**Q: What is createRoot?**
A: The new React 18 entry point that enables concurrent features. Replaces `ReactDOM.render`.
```js
// React 17
ReactDOM.render(<App />, document.getElementById('root'))

// React 18
import { createRoot } from 'react-dom/client'
createRoot(document.getElementById('root')).render(<App />)
```

**Q: What is optimistic UI?**
A: Updating the UI immediately (assuming success) before the server confirms. If the server returns an error, roll back to the previous state.
```js
// 1. Update UI optimistically
setLiked(true)
setCount(c => c + 1)
try {
  await api.like(postId)
} catch {
  // 2. Rollback on error
  setLiked(false)
  setCount(c => c - 1)
}
```

**Q: What are React Server Components (RSC)?**
A: Components that run exclusively on the server — they can directly access databases, file systems, and secrets without sending any JavaScript to the client. Introduced in React 18 and popularized by Next.js 13+.
- Server Components: no hooks, no event handlers, zero bundle size
- Client Components: marked with `'use client'`, run in the browser, can use hooks

---

## TESTING

**Q: What is React Testing Library?**
A: Testing utility that renders React components and provides queries to find elements like a user would (by role, label, text). Encourages testing behavior over implementation.

**Q: getBy vs queryBy vs findBy?**
A:
- `getBy*` — synchronous, throws if not found
- `queryBy*` — synchronous, returns `null` if not found (use for "not present" assertions)
- `findBy*` — async (returns Promise), waits for element to appear

**Q: Why prefer getByRole over getByTestId?**
A: `getByRole` tests accessibility semantics. If a screen reader can't find the element by its role, your users with assistive technology can't either. `getByTestId` tests implementation detail.

**Q: What is userEvent vs fireEvent?**
A: `fireEvent` dispatches a single synthetic event. `userEvent` simulates the full sequence of events a real user triggers (pointerdown → mousedown → mouseup → click → focus, etc.). `userEvent` is more realistic and should be preferred.

**Q: How do you test async components?**
A:
- `await screen.findByText(...)` — waits for element to appear
- `await waitFor(() => expect(...))` — retries assertion until it passes
- `await waitForElementToBeRemoved(...)` — waits for element to disappear

**Q: How do you test custom hooks?**
A: Use `renderHook` from `@testing-library/react`:
```js
const { result } = renderHook(() => useCounter(5))
act(() => result.current.increment())
expect(result.current.count).toBe(6)
```

**Q: How do you mock API calls in React tests?**
A: Three main approaches:
1. `jest.fn().mockResolvedValue(...)` — mock global fetch
2. `jest.mock('../api')` — mock an entire module
3. MSW (Mock Service Worker) — intercept network requests at the service worker level (most realistic)

---

## PERFORMANCE

**Q: When should you NOT use useMemo/useCallback?**
A: When the computation is cheap. The memoization itself has a cost. Only use them when:
- The computation is provably expensive (profiler confirms it)
- You're passing the value/function to a React.memo-wrapped child
- Dependencies change rarely

**Q: What causes unnecessary re-renders?**
A:
- Parent re-renders causing all children to re-render
- New object/function references in props on every render
- Context value changing too broadly

**Q: What is React Profiler?**
A: Built-in DevTools tab that records render timings. Shows which components re-rendered, how long they took, and why they rendered.

---

## QUICK REFERENCE

**Hook decision guide:**
- Local UI state (toggle, form input) → `useState`
- Complex state logic, multiple sub-values → `useReducer`
- Shared state across component tree → `useContext`
- Sync with external system (fetch, DOM) → `useEffect`
- Cache expensive value → `useMemo`
- Stable function reference → `useCallback`
- DOM element or mutable value without re-render → `useRef`
- Low-priority state update → `useTransition`
- Defer value to slow child → `useDeferredValue`
