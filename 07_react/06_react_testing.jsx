// ============================================================
// React Testing Library — Comprehensive Guide
// ============================================================
// Setup: npm install --save-dev @testing-library/react
//                               @testing-library/jest-dom
//                               @testing-library/user-event
//                               jest (or vitest)
//
// In jest.config.js add: setupFilesAfterFramework: ['@testing-library/jest-dom']
// ============================================================

import React, { useState, useEffect, useReducer } from 'react';
import {
  render,
  screen,
  fireEvent,
  waitFor,
  waitForElementToBeRemoved,
  within,
  act,
} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { renderHook, act as hookAct } from '@testing-library/react';
import '@testing-library/jest-dom'; // extends expect with DOM matchers


// ============================================================
// COMPONENTS UNDER TEST
// ============================================================

// --- Simple Counter ---
function Counter({ initialCount = 0 }) {
  const [count, setCount] = useState(initialCount);
  return (
    <div>
      <p data-testid="count">Count: {count}</p>
      <button onClick={() => setCount(c => c + 1)}>Increment</button>
      <button onClick={() => setCount(c => c - 1)}>Decrement</button>
      <button onClick={() => setCount(0)}>Reset</button>
    </div>
  );
}

// --- Greeting (conditional render) ---
function Greeting({ name }) {
  if (!name) return <p>Hello, stranger!</p>;
  return <p>Hello, {name}!</p>;
}

// --- Toggle Component ---
function Toggle() {
  const [on, setOn] = useState(false);
  return (
    <div>
      <p role="status">{on ? 'ON' : 'OFF'}</p>
      <button onClick={() => setOn(v => !v)} aria-pressed={on}>
        Toggle
      </button>
    </div>
  );
}

// --- Async Component — fetches user data ---
function UserProfile({ userId }) {
  const [user,    setUser]    = useState(null);
  const [loading, setLoading] = useState(true);
  const [error,   setError]   = useState(null);

  useEffect(() => {
    setLoading(true);
    fetch(`/api/users/${userId}`)
      .then(r => r.json())
      .then(data => { setUser(data); setLoading(false); })
      .catch(err => { setError(err.message); setLoading(false); });
  }, [userId]);

  if (loading) return <p>Loading...</p>;
  if (error)   return <p role="alert">Error: {error}</p>;
  return (
    <div>
      <h2>{user.name}</h2>
      <p>{user.email}</p>
    </div>
  );
}

// --- Registration Form ---
function RegistrationForm({ onSubmit }) {
  const [form, setForm] = useState({ username: '', email: '', password: '' });
  const [errors, setErrors] = useState({});

  function validate() {
    const e = {};
    if (!form.username) e.username = 'Username is required';
    if (!form.email.includes('@')) e.email = 'Invalid email';
    if (form.password.length < 6) e.password = 'Password must be at least 6 characters';
    return e;
  }

  function handleSubmit(e) {
    e.preventDefault();
    const errs = validate();
    if (Object.keys(errs).length > 0) {
      setErrors(errs);
      return;
    }
    onSubmit(form);
  }

  return (
    <form onSubmit={handleSubmit} aria-label="Registration form">
      <div>
        <label htmlFor="username">Username</label>
        <input
          id="username"
          value={form.username}
          onChange={e => setForm(f => ({ ...f, username: e.target.value }))}
          aria-describedby="username-error"
        />
        {errors.username && <span id="username-error" role="alert">{errors.username}</span>}
      </div>

      <div>
        <label htmlFor="email">Email</label>
        <input
          id="email"
          type="email"
          value={form.email}
          onChange={e => setForm(f => ({ ...f, email: e.target.value }))}
          aria-describedby="email-error"
        />
        {errors.email && <span id="email-error" role="alert">{errors.email}</span>}
      </div>

      <div>
        <label htmlFor="password">Password</label>
        <input
          id="password"
          type="password"
          value={form.password}
          onChange={e => setForm(f => ({ ...f, password: e.target.value }))}
          aria-describedby="password-error"
        />
        {errors.password && <span id="password-error" role="alert">{errors.password}</span>}
      </div>

      <button type="submit">Register</button>
    </form>
  );
}

// --- Custom Hook ---
function useCounter(initialValue = 0) {
  const [count, setCount] = useState(initialValue);
  const increment = () => setCount(c => c + 1);
  const decrement = () => setCount(c => c - 1);
  const reset     = () => setCount(initialValue);
  return { count, increment, decrement, reset };
}

// --- Async Custom Hook ---
function useFetchUser(userId) {
  const [state, dispatch] = useReducer(
    (s, a) => {
      switch (a.type) {
        case 'LOADING': return { ...s, loading: true, error: null };
        case 'SUCCESS': return { loading: false, error: null, user: a.payload };
        case 'ERROR':   return { loading: false, error: a.payload, user: null };
        default:        return s;
      }
    },
    { loading: false, user: null, error: null }
  );

  useEffect(() => {
    if (!userId) return;
    dispatch({ type: 'LOADING' });
    fetch(`/api/users/${userId}`)
      .then(r => r.json())
      .then(data => dispatch({ type: 'SUCCESS', payload: data }))
      .catch(err  => dispatch({ type: 'ERROR',   payload: err.message }));
  }, [userId]);

  return state;
}

// --- Select component ---
function ProductFilter({ products, onFilter }) {
  const [category, setCategory] = useState('all');

  function handleChange(e) {
    const val = e.target.value;
    setCategory(val);
    onFilter(val === 'all' ? products : products.filter(p => p.category === val));
  }

  return (
    <select value={category} onChange={handleChange} aria-label="Filter by category">
      <option value="all">All</option>
      <option value="electronics">Electronics</option>
      <option value="clothing">Clothing</option>
    </select>
  );
}


// ============================================================
// SECTION 1: BASICS — render, screen queries
// ============================================================

describe('Screen query types', () => {
  // getBy*    — throws if not found or > 1 found. Synchronous.
  // queryBy*  — returns null if not found (no throw). Good for "not present" assertions.
  // findBy*   — returns Promise (async), waits for element to appear.
  // getAllBy*, queryAllBy*, findAllBy* — return arrays

  test('getByText — find by text content', () => {
    render(<Greeting name="Alice" />);
    const el = screen.getByText('Hello, Alice!');
    expect(el).toBeInTheDocument();
  });

  test('getByRole — preferred way (accessible)', () => {
    render(<Counter />);
    const btn = screen.getByRole('button', { name: 'Increment' });
    expect(btn).toBeInTheDocument();
  });

  test('getByLabelText — find form inputs by label', () => {
    const mockSubmit = jest.fn();
    render(<RegistrationForm onSubmit={mockSubmit} />);
    const input = screen.getByLabelText('Username');
    expect(input).toBeInTheDocument();
  });

  test('getByPlaceholderText — find by placeholder', () => {
    render(<input placeholder="Search here..." />);
    expect(screen.getByPlaceholderText('Search here...')).toBeInTheDocument();
  });

  test('getByTestId — last resort (prefer role/text)', () => {
    render(<Counter />);
    expect(screen.getByTestId('count')).toHaveTextContent('Count: 0');
  });

  test('queryByText — assert element NOT present', () => {
    render(<Greeting />); // no name prop
    expect(screen.queryByText(/Hello, Alice/)).not.toBeInTheDocument();
    expect(screen.getByText('Hello, stranger!')).toBeInTheDocument();
  });

  test('getAllByRole — find multiple elements', () => {
    render(<Counter />);
    const buttons = screen.getAllByRole('button');
    expect(buttons).toHaveLength(3);
  });
});


// ============================================================
// SECTION 2: TESTING USER INTERACTIONS
// ============================================================

describe('Counter interactions — fireEvent (low-level)', () => {
  test('increments count on button click', () => {
    render(<Counter />);
    const incrementBtn = screen.getByRole('button', { name: 'Increment' });
    const countEl      = screen.getByTestId('count');

    expect(countEl).toHaveTextContent('Count: 0');
    fireEvent.click(incrementBtn);
    expect(countEl).toHaveTextContent('Count: 1');
    fireEvent.click(incrementBtn);
    expect(countEl).toHaveTextContent('Count: 2');
  });

  test('decrements count', () => {
    render(<Counter initialCount={5} />);
    fireEvent.click(screen.getByRole('button', { name: 'Decrement' }));
    expect(screen.getByTestId('count')).toHaveTextContent('Count: 4');
  });

  test('resets to initial value', () => {
    render(<Counter initialCount={10} />);
    fireEvent.click(screen.getByRole('button', { name: 'Increment' }));
    fireEvent.click(screen.getByRole('button', { name: 'Reset' }));
    expect(screen.getByTestId('count')).toHaveTextContent('Count: 0');
  });
});

describe('Counter interactions — userEvent (realistic, preferred)', () => {
  // userEvent simulates real browser events (pointerdown, mousedown, click, etc.)
  // Always use userEvent.setup() in React 18
  test('increments on click using userEvent', async () => {
    const user = userEvent.setup();
    render(<Counter />);

    await user.click(screen.getByRole('button', { name: 'Increment' }));
    expect(screen.getByTestId('count')).toHaveTextContent('Count: 1');
  });

  test('toggle button changes state', async () => {
    const user = userEvent.setup();
    render(<Toggle />);

    expect(screen.getByRole('status')).toHaveTextContent('OFF');
    await user.click(screen.getByRole('button', { name: 'Toggle' }));
    expect(screen.getByRole('status')).toHaveTextContent('ON');
    await user.click(screen.getByRole('button', { name: 'Toggle' }));
    expect(screen.getByRole('status')).toHaveTextContent('OFF');
  });

  test('type into input field', async () => {
    const user = userEvent.setup();
    render(<input placeholder="Name" aria-label="Name" />);

    const input = screen.getByRole('textbox', { name: 'Name' });
    await user.type(input, 'Hello World');
    expect(input).toHaveValue('Hello World');
  });

  test('clear and retype', async () => {
    const user = userEvent.setup();
    render(<input defaultValue="old value" aria-label="Field" />);

    const input = screen.getByRole('textbox', { name: 'Field' });
    await user.clear(input);
    await user.type(input, 'new value');
    expect(input).toHaveValue('new value');
  });

  test('keyboard interactions', async () => {
    const user = userEvent.setup();
    const onKeyDown = jest.fn();
    render(<input aria-label="Input" onKeyDown={onKeyDown} />);

    const input = screen.getByRole('textbox', { name: 'Input' });
    await user.click(input);
    await user.keyboard('{Enter}');
    expect(onKeyDown).toHaveBeenCalledWith(expect.objectContaining({ key: 'Enter' }));
  });

  test('tab through form elements', async () => {
    const user = userEvent.setup();
    render(
      <form>
        <input aria-label="First" />
        <input aria-label="Second" />
        <button>Submit</button>
      </form>
    );

    await user.tab(); // focus first input
    expect(screen.getByRole('textbox', { name: 'First' })).toHaveFocus();
    await user.tab(); // focus second input
    expect(screen.getByRole('textbox', { name: 'Second' })).toHaveFocus();
  });

  test('select dropdown option', async () => {
    const user = userEvent.setup();
    const onFilter = jest.fn();
    const products = [
      { id: 1, name: 'Phone', category: 'electronics' },
      { id: 2, name: 'Shirt', category: 'clothing' },
    ];

    render(<ProductFilter products={products} onFilter={onFilter} />);

    await user.selectOptions(screen.getByRole('combobox'), 'electronics');
    expect(onFilter).toHaveBeenCalledWith([{ id: 1, name: 'Phone', category: 'electronics' }]);
  });
});


// ============================================================
// SECTION 3: TESTING ASYNC COMPONENTS
// ============================================================

describe('Async component — UserProfile', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  // --- findBy* waits for element to appear (returns Promise) ---
  test('shows user data after loading', async () => {
    // Mock the global fetch
    global.fetch = jest.fn().mockResolvedValueOnce({
      json: async () => ({ name: 'Alice', email: 'alice@example.com' }),
    });

    render(<UserProfile userId={1} />);

    // Initially shows loading
    expect(screen.getByText('Loading...')).toBeInTheDocument();

    // Wait for the user name to appear (findBy* retries until timeout)
    const nameEl = await screen.findByRole('heading', { name: 'Alice' });
    expect(nameEl).toBeInTheDocument();
    expect(screen.getByText('alice@example.com')).toBeInTheDocument();
    expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
  });

  // --- waitFor — retries assertion until it passes ---
  test('shows error on fetch failure', async () => {
    global.fetch = jest.fn().mockRejectedValueOnce(new Error('Network error'));

    render(<UserProfile userId={1} />);

    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent('Error: Network error');
    });
  });

  // --- waitForElementToBeRemoved ---
  test('loading indicator disappears after data loads', async () => {
    global.fetch = jest.fn().mockResolvedValueOnce({
      json: async () => ({ name: 'Bob', email: 'bob@example.com' }),
    });

    render(<UserProfile userId={2} />);

    // Wait for loading text to disappear
    await waitForElementToBeRemoved(() => screen.queryByText('Loading...'));
    expect(screen.getByText('Bob')).toBeInTheDocument();
  });

  // --- Testing re-fetch when prop changes ---
  test('re-fetches when userId changes', async () => {
    global.fetch = jest.fn()
      .mockResolvedValueOnce({ json: async () => ({ name: 'Alice', email: 'a@test.com' }) })
      .mockResolvedValueOnce({ json: async () => ({ name: 'Bob',   email: 'b@test.com' }) });

    const { rerender } = render(<UserProfile userId={1} />);
    await screen.findByText('Alice');

    rerender(<UserProfile userId={2} />);
    await screen.findByText('Bob');
    expect(global.fetch).toHaveBeenCalledTimes(2);
  });
});


// ============================================================
// SECTION 4: MOCKING API CALLS
// ============================================================

describe('API mocking patterns', () => {

  // --- Pattern 1: jest.fn() with mockResolvedValue ---
  test('mock fetch with resolved value', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ id: 1, name: 'Alice' }),
    });

    render(<UserProfile userId={1} />);
    await screen.findByText('Alice');
    expect(fetch).toHaveBeenCalledWith('/api/users/1');
  });

  // --- Pattern 2: Mock a module (axios, api client) ---
  // In your test file:
  // jest.mock('../api/users', () => ({
  //   getUser: jest.fn(),
  // }))
  // import { getUser } from '../api/users'
  // getUser.mockResolvedValue({ name: 'Alice' })

  // --- Pattern 3: Different responses per call ---
  test('mock fetch returning different data per call', async () => {
    global.fetch = jest.fn()
      .mockResolvedValueOnce({ json: async () => ({ name: 'First call' }) })
      .mockResolvedValueOnce({ json: async () => ({ name: 'Second call' }) })
      .mockRejectedValueOnce(new Error('Third call fails'));
    // Each subsequent call returns the next value in chain
  });

  // --- Pattern 4: Mock with MSW (Mock Service Worker) — most realistic ---
  // Install: npm install msw
  //
  // src/mocks/handlers.js:
  //   import { http, HttpResponse } from 'msw'
  //   export const handlers = [
  //     http.get('/api/users/:id', ({ params }) => {
  //       return HttpResponse.json({ id: params.id, name: 'Alice' })
  //     }),
  //   ]
  //
  // src/mocks/server.js:
  //   import { setupServer } from 'msw/node'
  //   import { handlers } from './handlers'
  //   export const server = setupServer(...handlers)
  //
  // In test setup (jest.setup.js):
  //   import { server } from './mocks/server'
  //   beforeAll(() => server.listen())
  //   afterEach(() => server.resetHandlers())
  //   afterAll(() => server.close())
  //
  // Override for specific test:
  //   server.use(http.get('/api/users/1', () => HttpResponse.json({ name: 'Bob' })))
});


// ============================================================
// SECTION 5: TESTING FORMS
// ============================================================

describe('RegistrationForm', () => {
  const setup = () => {
    const onSubmit = jest.fn();
    const utils = render(<RegistrationForm onSubmit={onSubmit} />);
    const user = userEvent.setup();

    const usernameInput = screen.getByLabelText('Username');
    const emailInput    = screen.getByLabelText('Email');
    const passwordInput = screen.getByLabelText('Password');
    const submitBtn     = screen.getByRole('button', { name: 'Register' });

    return { ...utils, user, onSubmit, usernameInput, emailInput, passwordInput, submitBtn };
  };

  test('renders all form fields', () => {
    setup();
    expect(screen.getByLabelText('Username')).toBeInTheDocument();
    expect(screen.getByLabelText('Email')).toBeInTheDocument();
    expect(screen.getByLabelText('Password')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Register' })).toBeInTheDocument();
  });

  test('shows validation errors on empty submit', async () => {
    const { user, submitBtn, onSubmit } = setup();

    await user.click(submitBtn);

    expect(screen.getByText('Username is required')).toBeInTheDocument();
    expect(screen.getByText('Invalid email')).toBeInTheDocument();
    expect(screen.getByText('Password must be at least 6 characters')).toBeInTheDocument();
    expect(onSubmit).not.toHaveBeenCalled();
  });

  test('calls onSubmit with form data when valid', async () => {
    const { user, usernameInput, emailInput, passwordInput, submitBtn, onSubmit } = setup();

    await user.type(usernameInput, 'alice');
    await user.type(emailInput, 'alice@example.com');
    await user.type(passwordInput, 'securepassword');
    await user.click(submitBtn);

    expect(onSubmit).toHaveBeenCalledWith({
      username: 'alice',
      email: 'alice@example.com',
      password: 'securepassword',
    });
    expect(onSubmit).toHaveBeenCalledTimes(1);
  });

  test('shows email validation error for invalid email', async () => {
    const { user, usernameInput, emailInput, passwordInput, submitBtn, onSubmit } = setup();

    await user.type(usernameInput, 'alice');
    await user.type(emailInput, 'not-an-email'); // invalid
    await user.type(passwordInput, 'securepass');
    await user.click(submitBtn);

    expect(screen.getByText('Invalid email')).toBeInTheDocument();
    expect(onSubmit).not.toHaveBeenCalled();
  });

  test('clears errors on valid submission', async () => {
    const { user, usernameInput, emailInput, passwordInput, submitBtn } = setup();

    // First submit: trigger errors
    await user.click(submitBtn);
    expect(screen.getByText('Username is required')).toBeInTheDocument();

    // Fill in valid data and resubmit
    await user.type(usernameInput, 'alice');
    await user.type(emailInput, 'alice@example.com');
    await user.type(passwordInput, 'securepassword');
    await user.click(submitBtn);

    expect(screen.queryByText('Username is required')).not.toBeInTheDocument();
  });
});


// ============================================================
// SECTION 6: TESTING CUSTOM HOOKS
// ============================================================

describe('useCounter custom hook', () => {
  test('initializes with default value of 0', () => {
    const { result } = renderHook(() => useCounter());
    expect(result.current.count).toBe(0);
  });

  test('initializes with custom value', () => {
    const { result } = renderHook(() => useCounter(10));
    expect(result.current.count).toBe(10);
  });

  test('increment increases count by 1', () => {
    const { result } = renderHook(() => useCounter());
    hookAct(() => result.current.increment());
    expect(result.current.count).toBe(1);
  });

  test('decrement decreases count by 1', () => {
    const { result } = renderHook(() => useCounter(5));
    hookAct(() => result.current.decrement());
    expect(result.current.count).toBe(4);
  });

  test('reset returns to initial value', () => {
    const { result } = renderHook(() => useCounter(5));
    hookAct(() => result.current.increment());
    hookAct(() => result.current.increment());
    expect(result.current.count).toBe(7);
    hookAct(() => result.current.reset());
    expect(result.current.count).toBe(5); // back to initialValue
  });

  test('hook can be rerendered with new initialValue (via rerender)', () => {
    const { result, rerender } = renderHook(
      ({ initial }) => useCounter(initial),
      { initialProps: { initial: 0 } }
    );
    expect(result.current.count).toBe(0);
    // Note: changing initial doesn't reset because useState only uses initialValue once
    rerender({ initial: 10 });
    // Count remains 0 — this tests that initial prop change doesn't reset hook state
    expect(result.current.count).toBe(0);
  });
});

describe('useFetchUser async hook', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('starts with loading true, no user, no error', () => {
    global.fetch = jest.fn(() => new Promise(() => {})); // never resolves
    const { result } = renderHook(() => useFetchUser(1));
    expect(result.current.loading).toBe(true);
    expect(result.current.user).toBeNull();
    expect(result.current.error).toBeNull();
  });

  test('sets user on successful fetch', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      json: async () => ({ id: 1, name: 'Alice' }),
    });

    const { result } = renderHook(() => useFetchUser(1));

    await waitFor(() => expect(result.current.loading).toBe(false));
    expect(result.current.user).toEqual({ id: 1, name: 'Alice' });
    expect(result.current.error).toBeNull();
  });

  test('sets error on failed fetch', async () => {
    global.fetch = jest.fn().mockRejectedValue(new Error('Server down'));

    const { result } = renderHook(() => useFetchUser(1));

    await waitFor(() => expect(result.current.loading).toBe(false));
    expect(result.current.error).toBe('Server down');
    expect(result.current.user).toBeNull();
  });

  test('does not fetch when userId is null', () => {
    global.fetch = jest.fn();
    renderHook(() => useFetchUser(null));
    expect(fetch).not.toHaveBeenCalled();
  });
});


// ============================================================
// SECTION 7: ADVANCED PATTERNS
// ============================================================

describe('Advanced testing patterns', () => {

  // --- within() — scoped queries ---
  test('within() for querying inside a specific container', () => {
    render(
      <ul>
        <li data-testid="item-1">
          <span>Alice</span>
          <button>Delete</button>
        </li>
        <li data-testid="item-2">
          <span>Bob</span>
          <button>Delete</button>
        </li>
      </ul>
    );

    // There are 2 "Delete" buttons — use within() to scope the query
    const item1 = screen.getByTestId('item-1');
    const deleteAlice = within(item1).getByRole('button', { name: 'Delete' });
    expect(deleteAlice).toBeInTheDocument();
  });

  // --- act() — wrap state-triggering code ---
  test('act() wraps state updates outside render/userEvent', () => {
    const { result } = renderHook(() => useState(0));
    act(() => {
      result.current[1](42); // setState
    });
    expect(result.current[0]).toBe(42);
  });

  // --- Testing with context ---
  test('component that uses context', async () => {
    const ThemeContext = React.createContext('light');
    function ThemedButton() {
      const theme = React.useContext(ThemeContext);
      return <button className={theme}>Themed</button>;
    }

    // Option 1: Wrap with provider in render
    render(
      <ThemeContext.Provider value="dark">
        <ThemedButton />
      </ThemeContext.Provider>
    );
    expect(screen.getByRole('button')).toHaveClass('dark');
  });

  // --- Custom render wrapper (for global providers) ---
  function renderWithProviders(ui, { theme = 'light' } = {}) {
    const ThemeContext = React.createContext('light');
    function Wrapper({ children }) {
      return (
        <ThemeContext.Provider value={theme}>
          {children}
        </ThemeContext.Provider>
      );
    }
    return render(ui, { wrapper: Wrapper });
  }

  // --- Testing error states ---
  test('shows error boundary fallback on crash', () => {
    // Suppress console.error for expected errors
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

    function CrashingComponent() {
      throw new Error('Boom!');
    }

    class ErrorBoundary extends React.Component {
      state = { hasError: false };
      static getDerivedStateFromError() { return { hasError: true }; }
      render() {
        return this.state.hasError
          ? <p role="alert">Something went wrong</p>
          : this.props.children;
      }
    }

    render(
      <ErrorBoundary>
        <CrashingComponent />
      </ErrorBoundary>
    );

    expect(screen.getByRole('alert')).toHaveTextContent('Something went wrong');
    consoleSpy.mockRestore();
  });

  // --- jest-dom matchers reference ---
  test('jest-dom matchers', () => {
    render(
      <div>
        <input type="checkbox" aria-label="Accept" defaultChecked />
        <button disabled>Submit</button>
        <input aria-label="Name" value="Alice" readOnly />
        <p style={{ display: 'none' }}>Hidden</p>
        <a href="/home">Home link</a>
        <input type="text" aria-label="Field" className="active" />
      </div>
    );

    expect(screen.getByRole('checkbox', { name: 'Accept' })).toBeChecked();
    expect(screen.getByRole('button', { name: 'Submit' })).toBeDisabled();
    expect(screen.getByRole('textbox', { name: 'Name' })).toHaveValue('Alice');
    expect(screen.getByText('Hidden')).not.toBeVisible();
    expect(screen.getByRole('link', { name: 'Home link' })).toHaveAttribute('href', '/home');
    expect(screen.getByRole('textbox', { name: 'Field' })).toHaveClass('active');
  });
});


/*
=================================================================
QUICK REFERENCE — React Testing Library

RENDER
  render(<Component />)             — render to virtual DOM
  render(<Component />, { wrapper }) — with context wrapper
  rerender(<Component newProp />)   — re-render with new props
  unmount()                         — unmount the component

SCREEN QUERIES (priority order: role > label > text > testId)
  getByRole(role, { name })         — button, heading, textbox, etc.
  getByLabelText(text)              — form elements via <label>
  getByText(text/regex)             — visible text content
  getByPlaceholderText(text)        — input placeholder
  getByTestId(id)                   — data-testid attribute (last resort)
  findBy*(...)                      — async, returns Promise
  queryBy*(...)                     — returns null if not found

USER EVENTS (preferred over fireEvent)
  const user = userEvent.setup()
  user.click(el)                    — full click simulation
  user.type(el, 'text')             — type characters one by one
  user.clear(el)                    — clear input value
  user.keyboard('{Enter}')          — keyboard interaction
  user.tab()                        — tab to next focusable
  user.selectOptions(el, 'value')   — select from dropdown
  user.hover(el) / user.unhover(el) — mouse hover

ASYNC UTILITIES
  await screen.findByText(...)      — wait for element to appear
  await waitFor(() => expect(...))  — retry assertion until pass
  await waitForElementToBeRemoved() — wait for element to disappear

HOOKS
  renderHook(() => useMyHook())     — test custom hooks
  act(() => { ... })                — wrap state updates

jest-dom MATCHERS
  toBeInTheDocument()
  toHaveTextContent('text')
  toHaveValue('value')
  toHaveClass('classname')
  toBeDisabled() / toBeEnabled()
  toBeChecked()
  toBeVisible() / not.toBeVisible()
  toHaveAttribute('attr', 'value')
  toHaveFocus()
=================================================================
*/
