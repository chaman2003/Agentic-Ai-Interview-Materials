/*
═══════════════════════════════════════════════════════════════════════════════
  ZUSTAND — COMPREHENSIVE GUIDE (BASICS TO ADVANCED)
═══════════════════════════════════════════════════════════════════════════════

Zustand: Simple, fast, and scalable state management
Think: A small, fast bear! 🐻 (Zustand = German for "state")

Why Zustand?
✅ Minimal boilerplate (no providers, actions, reducers)
✅ Works with or without React
✅ Fast (doesn't re-render unnecessarily)
✅ Small bundle size (~1KB)
✅ Easy to learn (15 minutes!)

*/

import { create } from 'zustand';
import { persist, devtools, combine } from 'zustand/middleware';

// ─── 1. ZUSTAND BASICS ─────────────────────────────────────────────────────

// Create a store
const useTodoStore = create((set, get) => ({
  // State
  todos: [],

  // Actions
  addTodo: (text) => set((state) => ({
    todos: [...state.todos, {
      id: Date.now(),
      text,
      completed: false
    }]
  })),

  toggleTodo: (id) => set((state) => ({
    todos: state.todos.map(todo =>
      todo.id === id ? { ...todo, completed: !todo.completed } : todo
    )
  })),

  deleteTodo: (id) => set((state) => ({
    todos: state.todos.filter(todo => todo.id !== id)
  })),

  // Computed values (getters)
  getCompletedCount: () => {
    return get().todos.filter(t => t.completed).length;
  }
}));

// Usage in React component (no Provider needed!)
function TodoApp() {
  // Select specific state (only re-renders when todos change)
  const todos = useTodoStore((state) => state.todos);
  const addTodo = useTodoStore((state) => state.addTodo);
  const toggleTodo = useTodoStore((state) => state.toggleTodo);
  const deleteTodo = useTodoStore((state) => state.deleteTodo);

  const [input, setInput] = React.useState('');

  const handleAdd = () => {
    if (input.trim()) {
      addTodo(input);
      setInput('');
    }
  };

  return (
    <div>
      <h1>Todo List (Zustand)</h1>

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
              onChange={() => toggleTodo(todo.id)}
            />
            <span style={{ textDecoration: todo.completed ? 'line-through' : 'none' }}>
              {todo.text}
            </span>
            <button onClick={() => deleteTodo(todo.id)}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );
}

// ─── 2. SELECTING STATE (PERFORMANCE) ──────────────────────────────────────

/*
IMPORTANT: Select only what you need to avoid unnecessary re-renders
*/

// ❌ BAD: Component re-renders on ANY state change
function TodoCount() {
  const store = useTodoStore(); // Subscribes to entire store!
  return <div>Total: {store.todos.length}</div>;
}

// ✅ GOOD: Component only re-renders when todos.length changes
function TodoCount() {
  const count = useTodoStore((state) => state.todos.length);
  return <div>Total: {count}</div>;
}

// ✅ EVEN BETTER: Select multiple values efficiently
function TodoStats() {
  const { total, completed, active } = useTodoStore((state) => ({
    total: state.todos.length,
    completed: state.todos.filter(t => t.completed).length,
    active: state.todos.filter(t => !t.completed).length
  }));

  return (
    <div>
      <p>Total: {total}</p>
      <p>Completed: {completed}</p>
      <p>Active: {active}</p>
    </div>
  );
}

// ─── 3. ASYNC ACTIONS ───────────────────────────────────────────────────────

const useUserStore = create((set, get) => ({
  user: null,
  loading: false,
  error: null,

  // Async action: Fetch user from API
  fetchUser: async (userId) => {
    set({ loading: true, error: null });

    try {
      const response = await fetch(`/api/users/${userId}`);
      const user = await response.json();

      set({ user, loading: false });
    } catch (error) {
      set({ error: error.message, loading: false });
    }
  },

  // Async action: Login
  login: async (email, password) => {
    set({ loading: true, error: null });

    try {
      const response = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });

      if (!response.ok) {
        throw new Error('Invalid credentials');
      }

      const { user, token } = await response.json();

      // Store token in localStorage
      localStorage.setItem('token', token);

      set({ user, loading: false });
    } catch (error) {
      set({ error: error.message, loading: false });
    }
  },

  logout: () => {
    localStorage.removeItem('token');
    set({ user: null });
  }
}));

// Usage
function LoginForm() {
  const { login, loading, error } = useUserStore();

  const handleSubmit = (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    login(formData.get('email'), formData.get('password'));
  };

  return (
    <form onSubmit={handleSubmit}>
      <input name="email" type="email" placeholder="Email" />
      <input name="password" type="password" placeholder="Password" />
      <button type="submit" disabled={loading}>
        {loading ? 'Logging in...' : 'Login'}
      </button>
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </form>
  );
}

// ─── 4. MIDDLEWARE: PERSIST ────────────────────────────────────────────────

/*
Persist middleware: Save state to localStorage automatically
*/

import { persist } from 'zustand/middleware';

const useTodoStore = create(
  persist(
    (set) => ({
      todos: [],
      addTodo: (text) => set((state) => ({
        todos: [...state.todos, { id: Date.now(), text, completed: false }]
      })),
      toggleTodo: (id) => set((state) => ({
        todos: state.todos.map(t => t.id === id ? { ...t, completed: !t.completed } : t)
      })),
      deleteTodo: (id) => set((state) => ({
        todos: state.todos.filter(t => t.id !== id)
      }))
    }),
    {
      name: 'todo-storage', // localStorage key
      // Optional: customize what to persist
      partialize: (state) => ({ todos: state.todos }) // Only persist todos
    }
  )
);

// ─── 5. MIDDLEWARE: DEVTOOLS ───────────────────────────────────────────────

/*
DevTools middleware: Debug with Redux DevTools extension
*/

import { devtools } from 'zustand/middleware';

const useTodoStore = create(
  devtools(
    (set) => ({
      todos: [],
      addTodo: (text) => set((state) => ({
        todos: [...state.todos, { id: Date.now(), text, completed: false }]
      }), false, 'addTodo'), // Action name for DevTools
      toggleTodo: (id) => set((state) => ({
        todos: state.todos.map(t => t.id === id ? { ...t, completed: !t.completed } : t)
      }), false, 'toggleTodo')
    }),
    { name: 'TodoStore' } // Store name in DevTools
  )
);

// ─── 6. COMBINING MIDDLEWARES ──────────────────────────────────────────────

/*
Stack multiple middlewares together
*/

const useTodoStore = create(
  devtools(
    persist(
      (set) => ({
        todos: [],
        addTodo: (text) => set((state) => ({
          todos: [...state.todos, { id: Date.now(), text, completed: false }]
        }))
      }),
      { name: 'todo-storage' }
    ),
    { name: 'TodoStore' }
  )
);

// ─── 7. ZUSTAND WITHOUT REACT ──────────────────────────────────────────────

/*
Zustand works outside React too!
*/

import { createStore } from 'zustand/vanilla';

// Create vanilla store
const todoStore = createStore((set) => ({
  todos: [],
  addTodo: (text) => set((state) => ({
    todos: [...state.todos, { id: Date.now(), text, completed: false }]
  }))
}));

// Subscribe to changes
const unsubscribe = todoStore.subscribe((state) => {
  console.log('State changed:', state);
});

// Get state
console.log(todoStore.getState());

// Dispatch action
todoStore.getState().addTodo('Learn Zustand');

// Unsubscribe
unsubscribe();

// ─── 8. SLICES PATTERN (ORGANIZE LARGE STORES) ────────────────────────────

/*
Split store into slices for better organization
*/

// User slice
const createUserSlice = (set) => ({
  user: null,
  login: (user) => set({ user }),
  logout: () => set({ user: null })
});

// Todo slice
const createTodoSlice = (set) => ({
  todos: [],
  addTodo: (text) => set((state) => ({
    todos: [...state.todos, { id: Date.now(), text, completed: false }]
  }))
});

// Settings slice
const createSettingsSlice = (set) => ({
  theme: 'light',
  setTheme: (theme) => set({ theme })
});

// Combine slices
const useAppStore = create((set) => ({
  ...createUserSlice(set),
  ...createTodoSlice(set),
  ...createSettingsSlice(set)
}));

// Usage
function App() {
  const user = useAppStore((state) => state.user);
  const theme = useAppStore((state) => state.theme);
  const logout = useAppStore((state) => state.logout);

  return (
    <div className={theme}>
      {user && <button onClick={logout}>Logout</button>}
    </div>
  );
}

// ─── 9. IMMER MIDDLEWARE (MUTABLE UPDATES) ─────────────────────────────────

/*
Immer middleware: Write "mutable" code that's actually immutable
*/

import { immer } from 'zustand/middleware/immer';

const useStore = create(
  immer((set) => ({
    todos: [],
    // With Immer, you can "mutate" state directly
    addTodo: (text) => set((state) => {
      state.todos.push({ id: Date.now(), text, completed: false });
    }),
    toggleTodo: (id) => set((state) => {
      const todo = state.todos.find(t => t.id === id);
      if (todo) {
        todo.completed = !todo.completed;
      }
    })
  }))
);

// ─── 10. COMPUTED VALUES (SELECTORS) ───────────────────────────────────────

/*
Create derived state with selectors
*/

const useStore = create((set, get) => ({
  todos: [],
  addTodo: (text) => set((state) => ({
    todos: [...state.todos, { id: Date.now(), text, completed: false }]
  })),

  // Selector: Get completed todos
  getCompletedTodos: () => {
    return get().todos.filter(t => t.completed);
  },

  // Selector: Get active todos
  getActiveTodos: () => {
    return get().todos.filter(t => !t.completed);
  },

  // Selector: Get todo by ID
  getTodoById: (id) => {
    return get().todos.find(t => t.id === id);
  }
}));

// Usage
function TodoStats() {
  const getCompletedTodos = useStore((state) => state.getCompletedTodos);
  const completedTodos = getCompletedTodos();

  return <div>Completed: {completedTodos.length}</div>;
}

// ─── 11. TRANSIENT UPDATES (NO RE-RENDER) ─────────────────────────────────

/*
Update state without triggering re-render (for performance)
*/

const useStore = create((set) => ({
  mousePosition: { x: 0, y: 0 },
  setMousePosition: (x, y) => set({ mousePosition: { x, y } })
}));

// Transient update (doesn't trigger re-render)
useStore.setState({ mousePosition: { x: 100, y: 200 } }, true);

// ─── 12. ZUSTAND vs REDUX ──────────────────────────────────────────────────

/*
Zustand advantages:
✅ Less boilerplate (no actions, reducers, providers)
✅ Smaller bundle size (~1KB vs ~10KB)
✅ Simpler API (easier to learn)
✅ Better TypeScript support
✅ Can use outside React

Redux advantages:
✅ More mature ecosystem
✅ Better DevTools integration
✅ Time-travel debugging
✅ Middleware ecosystem (redux-saga, redux-observable)
✅ Community conventions

When to use Zustand:
- Small to medium apps
- Want simplicity
- Need good performance
- Don't need Redux ecosystem

When to use Redux:
- Large apps with complex state logic
- Team familiar with Redux
- Need time-travel debugging
- Using Redux ecosystem tools
*/

// ─── INTERVIEW SUMMARY ─────────────────────────────────────────────────────

/*
KEY CONCEPTS TO MEMORIZE:

1. CORE API:
   - create(): Creates a store
   - set(): Updates state
   - get(): Gets current state
   - No providers needed!

2. REACT HOOKS:
   - useStore(selector): Subscribe to state
   - Select only what you need for performance

3. MIDDLEWARE:
   - persist: Save to localStorage
   - devtools: Redux DevTools integration
   - immer: Mutable-style updates

4. PATTERNS:
   - Slices: Organize large stores
   - Selectors: Computed/derived state
   - Async actions: Regular async functions

5. PERFORMANCE:
   - Select specific state to avoid re-renders
   - Transient updates for high-frequency changes
   - No unnecessary Provider re-renders

6. BEST PRACTICES:
   - Keep stores small and focused
   - Use selectors for derived state
   - Combine middleware for persistence + devtools
   - Use slices pattern for large stores

COMMON INTERVIEW QUESTIONS:

Q: What is Zustand?
A: Lightweight state management library for React. Simple API, no boilerplate.

Q: Zustand vs Redux?
A: Zustand is simpler, smaller bundle, less boilerplate. Redux has bigger ecosystem.

Q: Zustand vs Context API?
A: Zustand has better performance, no provider hell, works outside React.

Q: How to persist state?
A: Use persist middleware with localStorage.

Q: How to handle async?
A: Regular async functions in actions (no special middleware needed).

Q: How to avoid re-renders?
A: Select only specific state you need in selector.

Q: Can Zustand work without React?
A: Yes! Use vanilla store (createStore from zustand/vanilla).

Q: How to split large store?
A: Use slices pattern to organize by feature/domain.

Q: How to debug Zustand?
A: Use devtools middleware with Redux DevTools extension.

Q: What's the bundle size?
A: ~1KB minified + gzipped (vs ~10KB for Redux).
*/

export {
  useTodoStore,
  useUserStore,
  useAppStore
};
