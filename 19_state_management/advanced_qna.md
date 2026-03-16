# State Management — Advanced Q&A

---

## REDUX ADVANCED

**Q: How does time-travel debugging work in Redux, step by step?**
A: Redux DevTools stores every dispatched action and a snapshot of state after each action.

Step-by-step:
1. Every action dispatched is appended to an `actionsById` map
2. State after each action is stored in a `computedStates` array
3. "Jump to action" replays all actions UP TO that point from the initial state
4. "Skip action" removes an action from the replay chain
5. "Commit" sets current state as the new initial state (clears history)
6. "Revert" goes back to the last committed state

**How it is implemented:** The DevTools wraps `dispatch` — every call is intercepted and logged. To replay, it calls `reducer(initialState, action1)`, then `reducer(result1, action2)`, etc.

**Why Redux enables this:** Pure reducers + immutable state = given the same initial state and sequence of actions, you ALWAYS get the same result. This is not possible with mutable state.

**Q: How do you write custom Redux middleware?**
A: Middleware is a higher-order function: `store => next => action => { ... }`

```js
// Logger middleware
const loggerMiddleware = store => next => action => {
  console.log('Dispatching:', action)
  console.log('State before:', store.getState())
  const result = next(action)  // pass to next middleware or reducer
  console.log('State after:', store.getState())
  return result
}

// Analytics middleware
const analyticsMiddleware = store => next => action => {
  if (action.type === 'USER_LOGIN') {
    analytics.track('login', { userId: action.payload.userId })
  }
  return next(action)
}

// Error catching middleware
const errorMiddleware = store => next => action => {
  try {
    return next(action)
  } catch (err) {
    Sentry.captureException(err, { extra: { action } })
    throw err
  }
}

// Request deduplication middleware
const dedupeMiddleware = (() => {
  const pendingRequests = new Set()
  return store => next => action => {
    if (action.type.endsWith('/pending')) {
      const key = action.type
      if (pendingRequests.has(key)) return  // skip duplicate
      pendingRequests.add(key)
      const result = next(action)
      result?.then?.(() => pendingRequests.delete(key))
      return result
    }
    return next(action)
  }
})()

// Apply middleware with configureStore
import { configureStore } from '@reduxjs/toolkit'
const store = configureStore({
  reducer: rootReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(loggerMiddleware, analyticsMiddleware),
})
```

**Q: How do you optimize Redux with Reselect?**
A: Reselect creates memoized selectors that only recompute when inputs change.

```js
import { createSelector } from 'reselect'

// Input selectors (simple, no memoization needed)
const selectTodos      = state => state.todos.items
const selectFilter     = state => state.todos.filter
const selectCurrentUser = state => state.auth.user

// Memoized selector — only recomputes when todos or filter changes
const selectFilteredTodos = createSelector(
  [selectTodos, selectFilter],
  (todos, filter) => {
    console.log('Computing filtered todos...')  // only logs when inputs change
    switch (filter) {
      case 'completed': return todos.filter(t => t.completed)
      case 'active':    return todos.filter(t => !t.completed)
      default:          return todos
    }
  }
)

// Composed selectors
const selectTodoStats = createSelector(
  [selectTodos],
  (todos) => ({
    total:     todos.length,
    completed: todos.filter(t => t.completed).length,
    active:    todos.filter(t => !t.completed).length,
  })
)

// Parametric selectors (factory pattern)
const makeSelectTodoById = (todoId) =>
  createSelector(
    [selectTodos],
    (todos) => todos.find(t => t.id === todoId)
  )

// In component — create selector instance per component
const selectMyTodo = useMemo(() => makeSelectTodoById(id), [id])
const todo = useSelector(selectMyTodo)
```

**Why Reselect?** Without memoization, every `useSelector` call creates a new derived value on every render, causing unnecessary re-renders of connected components.

**Q: What is RTK Query and how does it replace Redux async logic?**
A: RTK Query is a data fetching and caching tool built into Redux Toolkit. It auto-generates hooks for CRUD operations and handles caching, invalidation, loading/error state.

```js
import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'

export const usersApi = createApi({
  reducerPath: 'usersApi',
  baseQuery: fetchBaseQuery({ baseUrl: '/api' }),
  tagTypes: ['User'],
  endpoints: (builder) => ({
    getUsers: builder.query({
      query: () => '/users',
      providesTags: ['User'],
    }),
    getUserById: builder.query({
      query: (id) => `/users/${id}`,
      providesTags: (result, error, id) => [{ type: 'User', id }],
    }),
    createUser: builder.mutation({
      query: (body) => ({ url: '/users', method: 'POST', body }),
      invalidatesTags: ['User'],  // auto-refetch getUsers after creation
    }),
    updateUser: builder.mutation({
      query: ({ id, ...body }) => ({ url: `/users/${id}`, method: 'PATCH', body }),
      invalidatesTags: (result, error, { id }) => [{ type: 'User', id }],
    }),
  }),
})

// Auto-generated hooks:
export const {
  useGetUsersQuery,
  useGetUserByIdQuery,
  useCreateUserMutation,
  useUpdateUserMutation,
} = usersApi

// Usage in component:
function UserList() {
  const { data: users, isLoading, error } = useGetUsersQuery()
  const [createUser] = useCreateUserMutation()

  if (isLoading) return <Spinner />
  if (error) return <Error />
  return <ul>{users.map(u => <li key={u.id}>{u.name}</li>)}</ul>
}
```

---

## ZUSTAND ADVANCED

**Q: What are subscription patterns in Zustand?**
A: Zustand's `subscribe` method lets you listen to state changes outside of React (in services, utilities):

```js
import { create } from 'zustand'
import { subscribeWithSelector } from 'zustand/middleware'

const useStore = create(
  subscribeWithSelector((set) => ({
    count: 0,
    user: null,
    increment: () => set(s => ({ count: s.count + 1 })),
  }))
)

// Subscribe to ALL state changes
const unsubscribe = useStore.subscribe(
  state => console.log('State changed:', state)
)
unsubscribe() // clean up

// Subscribe to SPECIFIC slice (with subscribeWithSelector middleware)
const unsubCount = useStore.subscribe(
  state => state.count,              // selector
  (count, prevCount) => {            // callback
    console.log(`Count changed: ${prevCount} → ${count}`)
    if (count > 100) analytics.track('count_high')
  }
)

// Subscribe with equality check
useStore.subscribe(
  state => state.user,
  (user) => { if (user) startSession(user) },
  { equalityFn: (a, b) => a?.id === b?.id }  // custom equality
)
```

**Q: What are transient updates in Zustand?**
A: Accessing the latest state without subscribing (no re-render). Useful for high-frequency updates like mouse positions or scroll positions.

```js
const useMouseStore = create((set) => ({
  x: 0,
  y: 0,
  setPosition: (x, y) => set({ x, y }),
}))

// Anti-pattern: re-renders on every mouse move
function TrailEffect() {
  const { x, y } = useMouseStore()  // causes thousands of re-renders!
  // ...
}

// Transient update pattern: read state without subscribing
function TrailEffect() {
  const canvasRef = useRef()

  useEffect(() => {
    const canvas = canvasRef.current
    // Access state directly from store (no subscription = no re-render)
    const unsubscribe = useMouseStore.subscribe(
      state => state,
      ({ x, y }) => {
        // Draw directly on canvas without React re-render
        const ctx = canvas.getContext('2d')
        ctx.fillRect(x, y, 4, 4)
      }
    )
    return unsubscribe
  }, [])

  return <canvas ref={canvasRef} />
}
```

**Q: How do you combine Zustand with React Query?**
A: React Query manages SERVER state; Zustand manages CLIENT/UI state. They complement each other perfectly.

```js
// Zustand: client state (UI, filters, selections)
const useUIStore = create((set) => ({
  selectedUserId: null,
  filterStatus: 'all',
  sidebarOpen: false,
  selectUser: (id) => set({ selectedUserId: id }),
  setFilter: (status) => set({ filterStatus: status }),
}))

// React Query: server state (data from API)
function UserDashboard() {
  const { selectedUserId, filterStatus, selectUser } = useUIStore()

  // React Query fetches and caches server data
  const { data: users, isLoading } = useQuery({
    queryKey: ['users', filterStatus],
    queryFn: () => fetchUsers({ status: filterStatus }),
  })

  const { data: selectedUser } = useQuery({
    queryKey: ['user', selectedUserId],
    queryFn: () => fetchUser(selectedUserId),
    enabled: !!selectedUserId,  // only fetch when user is selected
  })

  return (
    <div>
      <UserList users={users} onSelect={selectUser} />
      {selectedUser && <UserDetail user={selectedUser} />}
    </div>
  )
}
```

---

## JOTAI vs RECOIL

**Q: What is Jotai?**
A: Atomic state management for React. State is split into small "atoms". Components subscribe only to the atoms they use → fine-grained re-renders.

```js
import { atom, useAtom, useAtomValue, useSetAtom } from 'jotai'

// Define atoms (like useState but global)
const countAtom    = atom(0)
const nameAtom     = atom('Alice')

// Derived atom (like useMemo but global)
const doubledAtom  = atom(get => get(countAtom) * 2)

// Writable derived atom
const uppercaseNameAtom = atom(
  get => get(nameAtom).toUpperCase(),
  (get, set, newName) => set(nameAtom, newName.toLowerCase())
)

// Async atom
const userAtom = atom(async (get) => {
  const id = get(userIdAtom)
  const res = await fetch(`/api/users/${id}`)
  return res.json()
})

// Usage
function Counter() {
  const [count, setCount] = useAtom(countAtom)
  const doubled = useAtomValue(doubledAtom)  // read-only
  const setName = useSetAtom(nameAtom)       // write-only

  return (
    <button onClick={() => setCount(c => c + 1)}>
      {count} (doubled: {doubled})
    </button>
  )
}
```

**Q: What is Recoil?**
A: Facebook's atomic state management library (now deprecated in favor of Jotai-like patterns). Uses atoms and selectors. More complex than Jotai with `RecoilRoot` requirement.

**Q: Jotai vs Recoil comparison?**
A:
| Feature | Jotai | Recoil |
|---------|-------|--------|
| Bundle size | ~3KB | ~22KB |
| Provider required | No (optional) | Yes (RecoilRoot) |
| Status | Active | Deprecated by Meta |
| Learning curve | Low | Medium |
| Async support | Built-in | Built-in (selectors) |
| Key management | No string keys needed | String keys required |
| TypeScript | Excellent | Good |

**Jotai is now preferred over Recoil** due to smaller size, no string keys, and active maintenance.

---

## REACT QUERY / TANSTACK QUERY

**Q: Server state vs client state — what is the difference?**
A:
- **Client state** — UI-only data (modal open, selected tab, form values). You own it. Managed with useState/Zustand/Redux.
- **Server state** — data from the server (users, posts, orders). You don't own it; it can change without your knowledge. Needs: caching, refetching, deduplication, synchronization.

React Query is designed specifically for server state. Don't use Redux for server state.

**Q: What are React Query's caching strategies?**
A:

```js
useQuery({
  queryKey: ['user', id],
  queryFn: () => fetchUser(id),
  staleTime: 5 * 60 * 1000,   // data is "fresh" for 5 minutes, no refetch
  gcTime: 10 * 60 * 1000,     // keep in cache for 10 minutes after unmount
  refetchOnWindowFocus: true,  // refetch when user comes back to tab
  refetchInterval: 30000,      // poll every 30 seconds
  retry: 3,                    // retry failed requests 3 times
  retryDelay: attemptIndex => Math.min(1000 * 2 ** attemptIndex, 30000), // exponential backoff
})
```

**staleTime** = how long data is considered fresh (no background refetch)
**gcTime** (cacheTime in v4) = how long unused cache entry persists in memory

**Q: How do you implement optimistic updates with React Query?**
A:
```js
import { useQueryClient, useMutation } from '@tanstack/react-query'

function LikeButton({ postId }) {
  const queryClient = useQueryClient()

  const mutation = useMutation({
    mutationFn: (liked) => fetch(`/api/posts/${postId}/like`, {
      method: 'POST', body: JSON.stringify({ liked })
    }),

    onMutate: async (newLiked) => {
      // 1. Cancel any outgoing refetches (avoid overwriting our optimistic update)
      await queryClient.cancelQueries({ queryKey: ['post', postId] })

      // 2. Snapshot the previous value
      const previousPost = queryClient.getQueryData(['post', postId])

      // 3. Optimistically update the cache
      queryClient.setQueryData(['post', postId], (old) => ({
        ...old,
        liked: newLiked,
        likeCount: newLiked ? old.likeCount + 1 : old.likeCount - 1,
      }))

      // 4. Return context with the snapshot for rollback
      return { previousPost }
    },

    onError: (err, newLiked, context) => {
      // 5. Rollback to snapshot on error
      queryClient.setQueryData(['post', postId], context.previousPost)
    },

    onSettled: () => {
      // 6. Refetch after success or error
      queryClient.invalidateQueries({ queryKey: ['post', postId] })
    },
  })

  return <button onClick={() => mutation.mutate(!post.liked)}>Like</button>
}
```

**Q: How does React Query cache invalidation work?**
A:
```js
const queryClient = useQueryClient()

// Invalidate specific query → marks stale → refetches if component mounted
queryClient.invalidateQueries({ queryKey: ['users'] })

// Invalidate by prefix — invalidates users, users/1, users/2, etc.
queryClient.invalidateQueries({ queryKey: ['users'], exact: false })

// Remove from cache entirely
queryClient.removeQueries({ queryKey: ['user', id] })

// Manually set cache data (no fetch)
queryClient.setQueryData(['user', id], updatedUser)

// Prefetch — load data before it's needed
queryClient.prefetchQuery({
  queryKey: ['user', id],
  queryFn: () => fetchUser(id),
})
```

**Q: What are React Query mutations?**
A: `useMutation` handles data-changing operations (POST, PUT, DELETE). Unlike queries, mutations don't run automatically.
```js
const mutation = useMutation({
  mutationFn: (newTodo) => fetch('/api/todos', { method: 'POST', body: JSON.stringify(newTodo) }),
  onSuccess: () => queryClient.invalidateQueries({ queryKey: ['todos'] }),
  onError: (error) => toast.error(error.message),
})

mutation.mutate({ text: 'New todo' })
// mutation.isPending, mutation.isSuccess, mutation.isError
```

---

## SWR (stale-while-revalidate)

**Q: What is SWR?**
A: A React data fetching library by Vercel. The name comes from the HTTP cache-control strategy: show cached (stale) data while fetching fresh data in the background (revalidate).

```js
import useSWR from 'swr'

const fetcher = (url) => fetch(url).then(r => r.json())

function Profile() {
  const { data, error, isLoading, mutate } = useSWR('/api/user', fetcher, {
    refreshInterval: 3000,    // revalidate every 3 seconds
    revalidateOnFocus: true,  // revalidate when window gets focus
    dedupingInterval: 2000,   // deduplicate requests within 2 seconds
  })

  if (isLoading) return <Spinner />
  if (error) return <Error />

  return (
    <div>
      <p>{data.name}</p>
      <button onClick={() => mutate()}>Refresh</button>
    </div>
  )
}

// Optimistic update with SWR
async function updateName(name) {
  await mutate(
    fetch('/api/user', { method: 'PATCH', body: JSON.stringify({ name }) }),
    {
      optimisticData: { ...data, name },  // show optimistically
      rollbackOnError: true,              // revert if fails
      revalidate: true,                   // refetch after mutation
    }
  )
}
```

**SWR vs React Query:**
- SWR: Simpler API, lighter (~4KB), Vercel-optimized, less features
- React Query: More features (devtools, mutations, offline support, more cache control), bigger community

---

## CONTEXT API PITFALLS AND PERFORMANCE

**Q: What are Context API performance pitfalls?**
A:
1. **All consumers re-render on any value change** — even if they use only part of the context
2. **Provider re-renders propagate downward** — new object reference = all consumers re-render

```js
// BAD: New object on every render
function AppProvider({ children }) {
  const [user, setUser] = useState(null)
  const [theme, setTheme] = useState('light')

  return (
    <AppContext.Provider value={{ user, setUser, theme, setTheme }}>
      {children}
    </AppContext.Provider>
  )
  // Problem: ANY state change creates a new value object → ALL consumers re-render
}

// GOOD: Split into separate contexts
function UserProvider({ children }) {
  const [user, setUser] = useState(null)
  return (
    <UserContext.Provider value={useMemo(() => ({ user, setUser }), [user])}>
      {children}
    </UserContext.Provider>
  )
}

// GOOD: Memoize value to prevent unnecessary re-renders
function ThemeProvider({ children }) {
  const [theme, setTheme] = useState('light')
  const value = useMemo(() => ({ theme, setTheme }), [theme])
  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>
}

// GOOD: Separate state and dispatch contexts (dispatch never changes)
const StateCtx   = React.createContext()
const DispatchCtx = React.createContext()

function Store({ children }) {
  const [state, dispatch] = useReducer(reducer, initialState)
  return (
    <DispatchCtx.Provider value={dispatch}>   {/* stable — never re-renders */}
      <StateCtx.Provider value={state}>
        {children}
      </StateCtx.Provider>
    </DispatchCtx.Provider>
  )
}
```

**Q: When should you NOT use Context API?**
A:
- High-frequency updates (mouse position, scroll, animation) → use Zustand subscriptions
- Large state used by many components → use Redux or Zustand (no provider hell)
- When you need time-travel debugging → use Redux
- When state needs to be accessed outside React → use Zustand vanilla store

---

## STATE MACHINES (XSTATE)

**Q: What is XState and why use it?**
A: A library for modeling application logic as finite state machines (FSM) and statecharts. Eliminates invalid states and makes complex async flows predictable.

```js
import { createMachine, assign } from 'xstate'
import { useMachine } from '@xstate/react'

const fetchMachine = createMachine({
  id: 'fetch',
  initial: 'idle',
  context: { data: null, error: null },

  states: {
    idle: {
      on: { FETCH: 'loading' }  // FETCH event → go to loading
    },
    loading: {
      invoke: {
        src: (context, event) => fetch(`/api/users/${event.id}`).then(r => r.json()),
        onDone: {
          target: 'success',
          actions: assign({ data: (ctx, e) => e.data }),
        },
        onError: {
          target: 'failure',
          actions: assign({ error: (ctx, e) => e.data.message }),
        },
      }
    },
    success: {
      on: { FETCH: 'loading', RESET: 'idle' }
    },
    failure: {
      on: { RETRY: 'loading', RESET: 'idle' }
    }
  }
})

// Usage in React
function UserFetcher({ userId }) {
  const [state, send] = useMachine(fetchMachine)

  return (
    <div>
      {state.matches('idle')    && <button onClick={() => send({ type: 'FETCH', id: userId })}>Fetch</button>}
      {state.matches('loading') && <Spinner />}
      {state.matches('success') && <UserCard user={state.context.data} />}
      {state.matches('failure') && <Error msg={state.context.error} onRetry={() => send('RETRY')} />}
    </div>
  )
}
```

**Why XState?**
- Impossible states become impossible (can't be both loading AND success)
- Self-documenting: state diagram is the specification
- Excellent for multi-step forms, auth flows, shopping cart

---

## WHEN TO USE WHAT

**Q: Decision guide — which state management to use?**
A:

| Scenario | Solution |
|----------|----------|
| Local UI state (toggle, input) | `useState` |
| Complex local state (multi-step form) | `useReducer` |
| Share state across 2-3 nearby components | Lift state up |
| App-wide UI state (theme, sidebar open) | `useContext` |
| Server data (users, posts, API) | React Query / RTK Query |
| Medium app, minimal boilerplate | Zustand |
| Large app, complex logic, team project | Redux Toolkit |
| Complex async flows, multi-step processes | XState |
| Atomic, fine-grained reactivity | Jotai |
| Need time-travel debugging | Redux |
| Works outside React | Zustand (vanilla) |

**Q: Can you mix state management solutions?**
A: Yes, and it's recommended:
- **Zustand** for client/UI state
- **React Query** for server state
- **Context** for simple theme/locale
- **XState** for complex form or auth flows

They don't conflict. Each does its job best.

---

## TRICKY INTERVIEW SCENARIOS

**Q: Race conditions in async state updates — how to fix?**
A: Multiple async operations may resolve out of order. Solution: cancel outdated requests.
```js
useEffect(() => {
  let cancelled = false
  fetchUser(userId).then(user => {
    if (!cancelled) setUser(user)  // only update if still relevant
  })
  return () => { cancelled = true }  // cleanup on next render or unmount
}, [userId])

// Modern approach: AbortController
useEffect(() => {
  const controller = new AbortController()
  fetch(`/api/users/${userId}`, { signal: controller.signal })
    .then(r => r.json())
    .then(setUser)
    .catch(err => { if (err.name !== 'AbortError') setError(err) })
  return () => controller.abort()
}, [userId])
```

**Q: "Why do my updates feel slow in a large Redux app?"**
A: Common causes and fixes:
1. Selectors not memoized → use Reselect
2. Subscribing to too much state → select specific slices
3. Too many connected components at top level → normalize + use entity selectors
4. Immer is slow for large nested state → normalize state structure (flat, by ID)
5. `JSON.stringify` in reducers for debugging → remove in production

**Q: How do you handle auth state with React Query?**
A: Use React Query for fetching the current user and Zustand/Context for auth actions:
```js
// Fetch current user (React Query)
function useCurrentUser() {
  return useQuery({
    queryKey: ['currentUser'],
    queryFn: () => fetch('/api/me').then(r => r.ok ? r.json() : null),
    staleTime: Infinity,  // never auto-refetch auth state
    retry: false,
  })
}

// Login mutation clears and refetches
function useLogin() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (credentials) => fetch('/api/login', { method: 'POST', body: JSON.stringify(credentials) }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['currentUser'] }),
  })
}
```

**Q: Redux vs Zustand — what's the real performance difference?**
A: Zustand is faster for most apps because:
1. No Provider overhead (Context re-renders are avoided)
2. Selective subscriptions by default (Redux requires manual `useSelector`)
3. Smaller bundle (~1KB vs ~10KB for Redux + Redux Toolkit)

But Redux Toolkit with Reselect + normalized state can match Zustand performance in large apps. The gap matters more in small-medium apps.
