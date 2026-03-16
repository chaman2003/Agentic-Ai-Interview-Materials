# STATE MANAGEMENT Q&A — COMPREHENSIVE

## REDUX

**Q: What is Redux?**
A: Predictable state container for JavaScript apps. All state lives in a single store. Changes are made by dispatching actions to reducers.

**Q: Three core principles of Redux?**
A: 1) Single source of truth (one store)
   2) State is read-only (dispatch actions to change)
   3) Changes made with pure functions (reducers)

**Q: What's a reducer?**
A: Pure function that takes `(state, action)` and returns new state. Must not mutate state or have side effects.

**Q: What's an action?**
A: Plain JavaScript object with a `type` field (and optional `payload`). Describes "what happened".

**Q: What's an action creator?**
A: Function that returns an action object. Example: `const addTodo = (text) => ({ type: 'ADD_TODO', payload: text })`

**Q: Pure function vs impure function?**
A: Pure: Same inputs always give same output, no side effects (API calls, mutations).
   Impure: May have different outputs, causes side effects.

**Q: How to handle async in Redux?**
A: Use `createAsyncThunk` (Redux Toolkit) or middleware like redux-thunk. Actions are sync, middleware handles async.

**Q: When to use Redux vs Context API?**
A: Redux: Complex state logic, many components need state, time-travel debugging, large team.
   Context: Simple shared state (theme, user), small app, state only needed in small part of tree.

**Q: What's Redux Toolkit?**
A: Official, opinionated Redux toolset. Simplifies Redux with `configureStore`, `createSlice`, `createAsyncThunk`. Less boilerplate.

**Q: What's createSlice?**
A: Combines action creators + reducer into one. Uses Immer for "mutable" updates that are actually immutable.

**Q: What's a selector?**
A: Function that extracts/derives data from state. Example: `const selectCompletedTodos = (state) => state.todos.filter(t => t.completed)`

**Q: Why normalize state?**
A: Avoid nested duplication, easier updates, better performance. Store entities in flat objects by ID:
   `{ users: { 1: {...}, 2: {...} }, posts: { 101: {...} } }`

**Q: What's Reselect?**
A: Library for memoized selectors. Only recomputes when dependencies change. Improves performance.

**Q: What's middleware in Redux?**
A: Function that intercepts actions before they reach reducer. Signature: `store => next => action => { ... }`.
   Use cases: Logging, analytics, async logic.

**Q: What's Redux Persist?**
A: Saves Redux state to localStorage/AsyncStorage. State survives page refresh.

**Q: What are Redux DevTools?**
A: Browser extension for debugging Redux. Features: Time-travel debugging, action history, state diff.

**Q: Pros/cons of Redux?**
A: Pros: Centralized state, time-travel debugging, predictable, great DevTools.
   Cons: Boilerplate (without Redux Toolkit), learning curve, overkill for simple apps.

---

## ZUSTAND

**Q: What is Zustand?**
A: Lightweight state management library. Simple API, no providers, ~1KB bundle size. Works with or without React.

**Q: Zustand vs Redux?**
A: Zustand: Simpler, less boilerplate, smaller bundle (~1KB vs ~10KB), faster to learn.
   Redux: Bigger ecosystem, time-travel debugging, more mature, better middleware.

**Q: Zustand vs Context API?**
A: Zustand: Better performance (no provider re-renders), works outside React, simpler API.
   Context: Built into React, good for simple cases, but provider hell with multiple contexts.

**Q: How to create a Zustand store?**
A: ```js
   import { create } from 'zustand'

   const useStore = create((set) => ({
     count: 0,
     increment: () => set((state) => ({ count: state.count + 1 }))
   }))
   ```

**Q: How to use Zustand in React?**
A: ```js
   function Counter() {
     const count = useStore((state) => state.count)
     const increment = useStore((state) => state.increment)

     return <button onClick={increment}>{count}</button>
   }
   ```

**Q: How to avoid re-renders in Zustand?**
A: Select only specific state you need. Don't select entire store.
   ❌ `const store = useStore()` (re-renders on any change)
   ✅ `const count = useStore(state => state.count)` (only re-renders when count changes)

**Q: How to persist Zustand state?**
A: Use persist middleware:
   ```js
   import { persist } from 'zustand/middleware'

   const useStore = create(
     persist(
       (set) => ({ count: 0, increment: () => set(s => ({ count: s.count + 1 })) }),
       { name: 'counter-storage' }
     )
   )
   ```

**Q: How to handle async in Zustand?**
A: Regular async functions! No special middleware needed:
   ```js
   const useStore = create((set) => ({
     user: null,
     fetchUser: async (id) => {
       const user = await fetch(`/api/users/${id}`).then(r => r.json())
       set({ user })
     }
   }))
   ```

**Q: Can Zustand work without React?**
A: Yes! Use vanilla store:
   ```js
   import { createStore } from 'zustand/vanilla'

   const store = createStore((set) => ({ count: 0 }))
   store.getState()
   store.subscribe((state) => console.log(state))
   ```

**Q: What's the slices pattern in Zustand?**
A: Split large store into smaller slices by feature/domain:
   ```js
   const createUserSlice = (set) => ({
     user: null,
     login: (user) => set({ user })
   })

   const createTodoSlice = (set) => ({
     todos: [],
     addTodo: (text) => set(s => ({ todos: [...s.todos, text] }))
   })

   const useStore = create((set) => ({
     ...createUserSlice(set),
     ...createTodoSlice(set)
   }))
   ```

**Q: What middlewares does Zustand have?**
A: - persist: Save to localStorage
   - devtools: Redux DevTools integration
   - immer: Mutable-style updates
   - combine: Type-safe state + actions separation

**Q: How to use Redux DevTools with Zustand?**
A: ```js
   import { devtools } from 'zustand/middleware'

   const useStore = create(
     devtools((set) => ({ ... }), { name: 'MyStore' })
   )
   ```

**Q: What's Immer middleware in Zustand?**
A: Allows "mutable" updates that are actually immutable:
   ```js
   import { immer } from 'zustand/middleware/immer'

   const useStore = create(
     immer((set) => ({
       todos: [],
       addTodo: (text) => set((state) => {
         state.todos.push(text) // "Mutate" directly!
       })
     }))
   )
   ```

**Q: How to compute derived state in Zustand?**
A: Use selectors or getter methods:
   ```js
   const useStore = create((set, get) => ({
     todos: [],
     getCompletedCount: () => get().todos.filter(t => t.completed).length
   }))
   ```

**Q: Zustand bundle size?**
A: ~1KB minified + gzipped (Redux ~10KB).

**Q: When to use Zustand?**
A: ✅ Small to medium apps
   ✅ Want simplicity and minimal boilerplate
   ✅ Good performance is priority
   ✅ Don't need Redux ecosystem

**Q: When to use Redux instead?**
A: ✅ Large apps with complex state logic
   ✅ Team familiar with Redux patterns
   ✅ Need time-travel debugging
   ✅ Using Redux ecosystem (saga, observable)

---

## GENERAL STATE MANAGEMENT

**Q: What is state management?**
A: Managing data that changes over time across your app. Deciding where state lives, how it updates, and how components access it.

**Q: Component state vs global state?**
A: Component state: Local to one component (useState, useReducer). Example: Form input, toggle.
   Global state: Shared across multiple components. Example: User auth, theme, shopping cart.

**Q: When to lift state up?**
A: When multiple components need to share the same state. Move state to their common parent.

**Q: What's prop drilling?**
A: Passing props through many layers of components just to reach a deeply nested child. Annoying and hard to maintain.
   Solution: Context API, Redux, Zustand.

**Q: What's the Observer pattern?**
A: Design pattern where observers subscribe to subject. When subject changes, all observers are notified.
   Redux/Zustand use this pattern (components subscribe to store).

**Q: What's immutability?**
A: Never mutating state directly. Always create new objects/arrays.
   ❌ `state.count++`
   ✅ `{ ...state, count: state.count + 1 }`

**Q: Why is immutability important?**
A: - React compares references to detect changes (===)
   - Enables time-travel debugging
   - Prevents bugs from unexpected mutations
   - Required for Redux reducers

**Q: What's React Context API?**
A: Built-in way to pass data through component tree without prop drilling.
   ```js
   const ThemeContext = React.createContext()

   <ThemeContext.Provider value={theme}>
     <App />
   </ThemeContext.Provider>
   ```

**Q: Context API pitfalls?**
A: - All consumers re-render when value changes (even if they don't use changed part)
   - Provider hell (wrapping app with many Providers)
   - Performance issues with frequent updates

**Q: Local state vs Redux/Zustand?**
A: Local state (useState): UI state, form inputs, toggles.
   Global state (Redux/Zustand): Auth, user profile, shopping cart, notifications.

   Rule: Keep state as local as possible. Only global when needed by multiple components.

**Q: What's optimistic updates?**
A: Update UI immediately before server confirms. If server fails, roll back.
   Example: Like button turns blue immediately, then server confirms.

**Q: What's pessimistic updates?**
A: Wait for server confirmation before updating UI. Slower but safer.

**Q: Client state vs server state?**
A: Client state: UI-only (theme, modal open, form values). Managed by Redux/Zustand.
   Server state: Data from backend (users, posts). Managed by React Query, SWR.

**Q: What's React Query / SWR?**
A: Libraries for managing server state. Handle caching, refetching, deduplication.
   Different from Redux/Zustand (which manage client state).

**Q: How to debug state issues?**
A: - Redux DevTools (time-travel debugging)
   - console.log in reducers/actions
   - React DevTools (component state)
   - Add logging middleware

---

## ADVANCED / TRICKY

**Q: Race conditions in state updates?**
A: Multiple async operations completing out of order. Latest request might not be latest response.
   Solution: Cancellation tokens, request IDs, only update if still mounted.

**Q: Stale closures in state updates?**
A: When callback captures old state value:
   ```js
   const [count, setCount] = useState(0)

   useEffect(() => {
     const timer = setInterval(() => {
       setCount(count + 1) // Always uses initial count (0)!
     }, 1000)
     return () => clearInterval(timer)
   }, [])
   ```
   Solution: Use functional update: `setCount(c => c + 1)`

**Q: Memory leaks in state management?**
A: - Not unsubscribing from store
   - Not cleaning up intervals/timeouts
   - Holding references to unmounted components
   Solution: Clean up in useEffect return, unsubscribe from stores.

**Q: How to test Redux?**
A: - Test reducers: Pure functions, easy to test
   - Test actions: Just objects, test action creators
   - Test connected components: Mock store or use Provider
   - Test async: Mock api calls, check dispatched actions

**Q: How to test Zustand?**
A: - Extract store logic: Test as regular functions
   - Mock store: `useStore.setState({ ... })` in tests
   - Test components: Render with store

**Q: Middleware execution order?**
A: Outer → Inner → Reducer → Inner → Outer
   Example: logger → thunk → reducer → thunk → logger

**Q: Can you mutate state in Redux?**
A: NO in regular Redux (breaks immutability).
   YES in Redux Toolkit (uses Immer, converts to immutable).
