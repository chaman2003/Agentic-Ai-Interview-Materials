/*
═══════════════════════════════════════════════════════════════════════════════
  REDUX — COMPREHENSIVE GUIDE (BASICS TO ADVANCED)
═══════════════════════════════════════════════════════════════════════════════

Redux: Predictable state container for JavaScript apps
Think: Central store where all your app's data lives

Core concepts:
1. Store: Single source of truth (the big box holding all state)
2. Actions: Plain objects describing "what happened"
3. Reducers: Pure functions that take (state, action) → new state
4. Dispatch: Send actions to store

*/

// ─── 1. REDUX BASICS ───────────────────────────────────────────────────────

const { createStore } = require('redux');

// Action types (constants to avoid typos)
const ADD_TODO = 'ADD_TODO';
const TOGGLE_TODO = 'TOGGLE_TODO';
const DELETE_TODO = 'DELETE_TODO';

// Action creators (functions that return actions)
const addTodo = (text) => ({
  type: ADD_TODO,
  payload: {
    id: Date.now(),
    text,
    completed: false
  }
});

const toggleTodo = (id) => ({
  type: TOGGLE_TODO,
  payload: id
});

const deleteTodo = (id) => ({
  type: DELETE_TODO,
  payload: id
});

// Initial state
const initialState = {
  todos: []
};

// Reducer: Pure function (no side effects!)
function todoReducer(state = initialState, action) {
  switch (action.type) {
    case ADD_TODO:
      return {
        ...state,
        todos: [...state.todos, action.payload]
      };

    case TOGGLE_TODO:
      return {
        ...state,
        todos: state.todos.map(todo =>
          todo.id === action.payload
            ? { ...todo, completed: !todo.completed }
            : todo
        )
      };

    case DELETE_TODO:
      return {
        ...state,
        todos: state.todos.filter(todo => todo.id !== action.payload)
      };

    default:
      return state;
  }
}

// Create store
const store = createStore(todoReducer);

// Usage
store.dispatch(addTodo('Learn Redux'));
store.dispatch(addTodo('Build an app'));
console.log(store.getState()); // { todos: [...] }

store.dispatch(toggleTodo(1));
console.log(store.getState()); // First todo is now completed

// ─── 2. REDUX WITH REACT ───────────────────────────────────────────────────

/*
React-Redux: Official React bindings for Redux
Key APIs: Provider, useSelector, useDispatch
*/

import React from 'react';
import { Provider, useSelector, useDispatch } from 'react-redux';
import { createStore } from 'redux';

// Wrap app with Provider
function App() {
  return (
    <Provider store={store}>
      <TodoApp />
    </Provider>
  );
}

// Use hooks to access store
function TodoApp() {
  const todos = useSelector(state => state.todos);
  const dispatch = useDispatch();

  const [input, setInput] = React.useState('');

  const handleAdd = () => {
    if (input.trim()) {
      dispatch(addTodo(input));
      setInput('');
    }
  };

  return (
    <div>
      <h1>Todo List</h1>

      <input
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Add todo..."
      />
      <button onClick={handleAdd}>Add</button>

      <ul>
        {todos.map((todo) => (
          <li key={todo.id}>
            <input
              type="checkbox"
              checked={todo.completed}
              onChange={() => dispatch(toggleTodo(todo.id))}
            />
            <span style={{ textDecoration: todo.completed ? 'line-through' : 'none' }}>
              {todo.text}
            </span>
            <button onClick={() => dispatch(deleteTodo(todo.id))}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );
}

// ─── 3. REDUX TOOLKIT (MODERN REDUX) ───────────────────────────────────────

/*
Redux Toolkit: Official, opinionated Redux toolset
Simplifies Redux with less boilerplate

Key APIs:
- configureStore: Enhanced store setup
- createSlice: Combines actions + reducer
- createAsyncThunk: Handle async logic
*/

import { configureStore, createSlice, createAsyncThunk } from '@reduxjs/toolkit';

// Create slice (combines actions + reducer)
const todoSlice = createSlice({
  name: 'todos',
  initialState: {
    items: [],
    loading: false,
    error: null
  },
  reducers: {
    // Redux Toolkit uses Immer under the hood, so you can "mutate" state
    addTodo: (state, action) => {
      state.items.push(action.payload);
    },
    toggleTodo: (state, action) => {
      const todo = state.items.find(t => t.id === action.payload);
      if (todo) {
        todo.completed = !todo.completed;
      }
    },
    deleteTodo: (state, action) => {
      state.items = state.items.filter(t => t.id !== action.payload);
    }
  },
  extraReducers: (builder) => {
    // Handle async actions
    builder
      .addCase(fetchTodos.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchTodos.fulfilled, (state, action) => {
        state.loading = false;
        state.items = action.payload;
      })
      .addCase(fetchTodos.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      });
  }
});

// Async action (fetch todos from API)
const fetchTodos = createAsyncThunk(
  'todos/fetchTodos',
  async () => {
    const response = await fetch('/api/todos');
    return response.json();
  }
);

// Export actions
export const { addTodo, toggleTodo, deleteTodo } = todoSlice.actions;

// Configure store
const store = configureStore({
  reducer: {
    todos: todoSlice.reducer
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false // Disable if storing non-serializable data
    })
});

export default store;

// ─── 4. ADVANCED REDUX PATTERNS ────────────────────────────────────────────

// Pattern 1: Normalized state (avoid nested data)
/*
Bad:
{
  users: [
    { id: 1, name: 'Alice', posts: [{ id: 101, title: 'Post 1' }] }
  ]
}

Good:
{
  users: { 1: { id: 1, name: 'Alice', postIds: [101] } },
  posts: { 101: { id: 101, title: 'Post 1', userId: 1 } }
}
*/

import { createEntityAdapter } from '@reduxjs/toolkit';

// Entity adapter for normalized state
const usersAdapter = createEntityAdapter({
  selectId: (user) => user.id,
  sortComparer: (a, b) => a.name.localeCompare(b.name)
});

const usersSlice = createSlice({
  name: 'users',
  initialState: usersAdapter.getInitialState({
    loading: false
  }),
  reducers: {
    userAdded: usersAdapter.addOne,
    usersAdded: usersAdapter.addMany,
    userUpdated: usersAdapter.updateOne,
    userRemoved: usersAdapter.removeOne
  }
});

// Selectors
export const {
  selectAll: selectAllUsers,
  selectById: selectUserById,
  selectIds: selectUserIds
} = usersAdapter.getSelectors((state) => state.users);

// Pattern 2: Combining multiple slices
const rootReducer = {
  todos: todoSlice.reducer,
  users: usersSlice.reducer,
  auth: authSlice.reducer
};

const store = configureStore({
  reducer: rootReducer
});

// Pattern 3: Reselect (memoized selectors for performance)
import { createSelector } from '@reduxjs/toolkit';

// Basic selector
const selectTodos = (state) => state.todos.items;

// Memoized selector (only recomputes when todos change)
const selectCompletedTodos = createSelector(
  [selectTodos],
  (todos) => todos.filter(todo => todo.completed)
);

const selectActiveTodos = createSelector(
  [selectTodos],
  (todos) => todos.filter(todo => !todo.completed)
);

// Composed selector
const selectTodoStats = createSelector(
  [selectTodos, selectCompletedTodos, selectActiveTodos],
  (allTodos, completed, active) => ({
    total: allTodos.length,
    completed: completed.length,
    active: active.length,
    completionRate: allTodos.length > 0
      ? (completed.length / allTodos.length * 100).toFixed(1)
      : 0
  })
);

// Usage in component
function TodoStats() {
  const stats = useSelector(selectTodoStats);

  return (
    <div>
      <p>Total: {stats.total}</p>
      <p>Completed: {stats.completed}</p>
      <p>Active: {stats.active}</p>
      <p>Completion Rate: {stats.completionRate}%</p>
    </div>
  );
}

// ─── 5. REDUX MIDDLEWARE ───────────────────────────────────────────────────

/*
Middleware: Intercepts actions before they reach reducer
Use cases: Logging, async logic, analytics
*/

// Custom logger middleware
const loggerMiddleware = (store) => (next) => (action) => {
  console.log('Dispatching:', action);
  const result = next(action);
  console.log('Next state:', store.getState());
  return result;
};

// Custom analytics middleware
const analyticsMiddleware = (store) => (next) => (action) => {
  // Send action to analytics service
  if (action.type.startsWith('todos/')) {
    analytics.track('Todo Action', {
      action: action.type,
      payload: action.payload
    });
  }

  return next(action);
};

// Add middleware to store
const store = configureStore({
  reducer: rootReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(loggerMiddleware, analyticsMiddleware)
});

// ─── 6. REDUX PERSIST (STATE PERSISTENCE) ──────────────────────────────────

/*
Redux Persist: Save Redux state to localStorage/AsyncStorage
Survive page refreshes!
*/

import { persistStore, persistReducer } from 'redux-persist';
import storage from 'redux-persist/lib/storage'; // localStorage

const persistConfig = {
  key: 'root',
  storage,
  whitelist: ['todos', 'auth'], // Only persist these slices
  blacklist: ['ui'] // Don't persist UI state
};

const persistedReducer = persistReducer(persistConfig, rootReducer);

const store = configureStore({
  reducer: persistedReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST', 'persist/REHYDRATE']
      }
    })
});

const persistor = persistStore(store);

// Wrap app with PersistGate
import { PersistGate } from 'redux-persist/integration/react';

function App() {
  return (
    <Provider store={store}>
      <PersistGate loading={<div>Loading...</div>} persistor={persistor}>
        <TodoApp />
      </PersistGate>
    </Provider>
  );
}

// ─── 7. REDUX DEVTOOLS ─────────────────────────────────────────────────────

/*
Redux DevTools: Browser extension for debugging Redux
Features: Time-travel debugging, action history, state diff

Install: Chrome/Firefox extension "Redux DevTools"
*/

// Already enabled by default with configureStore!
// For manual setup:
const enhancers = window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__ || compose;
const store = createStore(reducer, enhancers(applyMiddleware(...middleware)));

// ─── 8. REDUX vs CONTEXT API ───────────────────────────────────────────────

/*
When to use Redux:
✅ Complex state logic (many actions, derived state)
✅ State needed across many parts of app
✅ Need time-travel debugging
✅ Large team (Redux enforces structure)

When to use Context API:
✅ Simple state (theme, user, locale)
✅ State only needed in small part of tree
✅ Small app or prototype
*/

// ─── INTERVIEW SUMMARY ─────────────────────────────────────────────────────

/*
KEY CONCEPTS TO MEMORIZE:

1. CORE PRINCIPLES:
   - Single source of truth (one store)
   - State is read-only (dispatch actions to change)
   - Changes made with pure functions (reducers)

2. REDUX FLOW:
   User clicks button → dispatch(action) → reducer(state, action) → new state → UI updates

3. REDUX TOOLKIT:
   - configureStore: Setup store with good defaults
   - createSlice: Combines actions + reducer
   - createAsyncThunk: Handle async operations
   - createEntityAdapter: Normalized state management

4. REACT HOOKS:
   - useSelector: Read state from store
   - useDispatch: Dispatch actions to store

5. ADVANCED:
   - Selectors: Extract derived state
   - Reselect: Memoized selectors for performance
   - Middleware: Intercept actions (logging, analytics)
   - Redux Persist: Save state to storage

6. BEST PRACTICES:
   - Keep reducers pure (no side effects)
   - Normalize nested data
   - Use Redux Toolkit (less boilerplate)
   - Memoize expensive selectors
   - Keep UI state in component, global state in Redux

COMMON INTERVIEW QUESTIONS:

Q: What is Redux?
A: Predictable state container. Central store for all app state.

Q: Why Redux over useState?
A: Centralized state, easier to debug, time-travel, complex state logic.

Q: What's a reducer?
A: Pure function that takes (state, action) and returns new state.

Q: What's an action?
A: Plain object with 'type' field describing what happened.

Q: Redux vs Context API?
A: Redux for complex state, Context for simple shared state.

Q: What's Redux Toolkit?
A: Official toolset that simplifies Redux with less boilerplate.

Q: How to handle async in Redux?
A: createAsyncThunk or redux-thunk middleware.

Q: What's a selector?
A: Function that extracts/derives data from state.

Q: Why normalize state?
A: Avoid duplication, easier updates, better performance.

Q: What's middleware?
A: Function that intercepts actions before they reach reducer.
*/

export {
  store,
  addTodo,
  toggleTodo,
  deleteTodo,
  fetchTodos,
  selectTodoStats,
  selectCompletedTodos,
  selectActiveTodos
};
