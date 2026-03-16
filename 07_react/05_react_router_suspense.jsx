// ============================================================
// React Router v6 + Suspense + React 18 — Comprehensive Guide
// ============================================================

import React, {
  Suspense,
  lazy,
  useState,
  useTransition,
  useDeferredValue,
  startTransition,
  Component,
} from 'react';
import {
  BrowserRouter,
  Routes,
  Route,
  Link,
  NavLink,
  Navigate,
  Outlet,
  useNavigate,
  useParams,
  useSearchParams,
  useLocation,
} from 'react-router-dom';


// ============================================================
// SECTION 1: BASIC REACT ROUTER v6 SETUP
// ============================================================

// --- 1.1 Root Layout with nested routes ---
function RootLayout() {
  return (
    <div>
      <nav>
        {/* NavLink adds "active" class automatically when route matches */}
        <NavLink to="/" end style={({ isActive }) => ({ fontWeight: isActive ? 'bold' : 'normal' })}>
          Home
        </NavLink>
        <NavLink to="/about" style={({ isActive }) => ({ color: isActive ? 'tomato' : 'inherit' })}>
          About
        </NavLink>
        <NavLink to="/dashboard">Dashboard</NavLink>
        <NavLink to="/blog">Blog</NavLink>
        <NavLink to="/profile">Profile</NavLink>
      </nav>

      {/* Outlet renders the matched child route */}
      <main>
        <Outlet />
      </main>
    </div>
  );
}

// --- 1.2 Page Components ---
function HomePage() {
  return <h1>Home Page</h1>;
}

function AboutPage() {
  return <h1>About Page</h1>;
}

function NotFoundPage() {
  return <h1>404 — Page Not Found</h1>;
}


// ============================================================
// SECTION 2: useParams, useSearchParams, useNavigate, useLocation
// ============================================================

// --- 2.1 useParams — Extract URL path parameters ---
// Route: /blog/:category/:postId
function BlogPost() {
  const { category, postId } = useParams();
  // URL /blog/tech/42 => category="tech", postId="42"
  return (
    <div>
      <h2>Category: {category}</h2>
      <h3>Post ID: {postId}</h3>
    </div>
  );
}

// --- 2.2 useSearchParams — Read/Write query string ---
// URL: /blog?search=react&page=2
function BlogList() {
  const [searchParams, setSearchParams] = useSearchParams();

  const search = searchParams.get('search') || '';
  const page   = Number(searchParams.get('page')) || 1;

  function handleSearch(e) {
    setSearchParams({ search: e.target.value, page: 1 }); // updates URL query string
  }

  function nextPage() {
    setSearchParams({ search, page: page + 1 });
  }

  return (
    <div>
      <input value={search} onChange={handleSearch} placeholder="Search posts..." />
      <p>Page: {page}</p>
      <button onClick={nextPage}>Next Page</button>
    </div>
  );
}

// --- 2.3 useNavigate — Programmatic navigation ---
function LoginForm() {
  const navigate = useNavigate();
  const [username, setUsername] = useState('');

  async function handleSubmit(e) {
    e.preventDefault();
    const ok = await fakeLogin(username);
    if (ok) {
      navigate('/dashboard', { replace: true }); // replace: no back button to login
    } else {
      navigate('/login?error=invalid', { state: { from: '/login' } }); // pass state
    }
  }

  // navigate(-1)  => go back
  // navigate(1)   => go forward
  // navigate('/path', { replace: true })  => replace history entry

  return (
    <form onSubmit={handleSubmit}>
      <input value={username} onChange={e => setUsername(e.target.value)} />
      <button type="submit">Login</button>
      <button type="button" onClick={() => navigate(-1)}>Go Back</button>
    </form>
  );
}

async function fakeLogin(username) {
  return username === 'admin';
}

// --- 2.4 useLocation — Current URL info ---
function CurrentRouteInfo() {
  const location = useLocation();
  // location.pathname  => "/dashboard"
  // location.search    => "?tab=overview"
  // location.hash      => "#section1"
  // location.state     => { from: '/login' }  (passed via navigate)
  return (
    <pre>{JSON.stringify(location, null, 2)}</pre>
  );
}


// ============================================================
// SECTION 3: NESTED ROUTES + OUTLET
// ============================================================

// Dashboard has its own sub-routes
function DashboardLayout() {
  return (
    <div style={{ display: 'flex' }}>
      <aside>
        <Link to="/dashboard">Overview</Link>
        <Link to="/dashboard/settings">Settings</Link>
        <Link to="/dashboard/analytics">Analytics</Link>
      </aside>
      <section>
        {/* Child routes render here */}
        <Outlet />
      </section>
    </div>
  );
}

function DashboardOverview() { return <p>Welcome to Dashboard Overview</p>; }
function DashboardSettings() { return <p>Settings Page</p>; }
function DashboardAnalytics() { return <p>Analytics Page</p>; }


// ============================================================
// SECTION 4: PROTECTED ROUTES
// ============================================================

// Simulated auth context
const AuthContext = React.createContext(null);

function AuthProvider({ children }) {
  const [user, setUser] = useState(null); // null = not logged in

  const login  = (userData) => setUser(userData);
  const logout = ()         => setUser(null);

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

function useAuth() {
  return React.useContext(AuthContext);
}

// --- ProtectedRoute: redirect to /login if not authenticated ---
function ProtectedRoute({ children }) {
  const { user } = useAuth();
  const location = useLocation();

  if (!user) {
    // Redirect to login, but save the intended URL in state
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children;
}

// --- Role-based ProtectedRoute ---
function RoleProtectedRoute({ children, requiredRole }) {
  const { user } = useAuth();
  const location = useLocation();

  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (!user.roles?.includes(requiredRole)) {
    return <Navigate to="/unauthorized" replace />;
  }

  return children;
}

// --- Login page that redirects back to intended route ---
function LoginPage() {
  const { login } = useAuth();
  const navigate  = useNavigate();
  const location  = useLocation();

  const from = location.state?.from?.pathname || '/dashboard';

  function handleLogin() {
    login({ id: 1, name: 'Alice', roles: ['user', 'admin'] });
    navigate(from, { replace: true }); // go back to where they came from
  }

  return (
    <div>
      <p>You must login to see: {from}</p>
      <button onClick={handleLogin}>Login as Alice</button>
    </div>
  );
}

function AdminPage() {
  const { user, logout } = useAuth();
  return (
    <div>
      <h2>Admin Page — Hi {user?.name}</h2>
      <button onClick={logout}>Logout</button>
    </div>
  );
}

function UnauthorizedPage() {
  return <h2>403 — You do not have permission to view this page</h2>;
}


// ============================================================
// SECTION 5: React.lazy + Suspense (Code Splitting)
// ============================================================

// Lazy-loaded components — only fetched when needed
// Each lazy() call creates a separate bundle chunk
const LazyDashboard = lazy(() => import('./Dashboard')); // hypothetical module
const LazyProfile   = lazy(() =>
  // Simulate delay for demo
  new Promise(resolve =>
    setTimeout(() => resolve({ default: () => <h2>Profile (lazy loaded)</h2> }), 800)
  )
);

// --- Suspense wraps lazy components with a fallback ---
function AppWithLazy() {
  return (
    <BrowserRouter>
      {/* Single Suspense wrapping all lazy routes */}
      <Suspense fallback={<GlobalSpinner />}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/dashboard" element={<LazyDashboard />} />
          <Route path="/profile"   element={<LazyProfile />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}

// --- Per-route Suspense boundaries (finer control) ---
function AppWithPerRouteSuspense() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route
          path="/dashboard"
          element={
            <Suspense fallback={<SkeletonDashboard />}>
              <LazyDashboard />
            </Suspense>
          }
        />
        <Route
          path="/profile"
          element={
            <Suspense fallback={<p>Loading profile...</p>}>
              <LazyProfile />
            </Suspense>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

function GlobalSpinner() {
  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
      <div className="spinner" />
    </div>
  );
}

function SkeletonDashboard() {
  return (
    <div className="skeleton">
      <div className="skeleton-header" style={{ height: 40, background: '#eee', marginBottom: 16 }} />
      <div className="skeleton-body"  style={{ height: 200, background: '#eee' }} />
    </div>
  );
}


// ============================================================
// SECTION 6: ERROR BOUNDARIES with Suspense
// ============================================================

// Error boundaries MUST be class components (as of React 18)
class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    // Log to error reporting service
    console.error('ErrorBoundary caught:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        this.props.fallback || (
          <div style={{ padding: 24, background: '#fee', borderRadius: 8 }}>
            <h2>Something went wrong</h2>
            <p>{this.state.error?.message}</p>
            <button onClick={() => this.setState({ hasError: false, error: null })}>
              Try Again
            </button>
          </div>
        )
      );
    }
    return this.props.children;
  }
}

// --- Combined ErrorBoundary + Suspense pattern ---
function SafeLazyRoute({ component: LazyComp, fallback, errorFallback }) {
  return (
    <ErrorBoundary fallback={errorFallback}>
      <Suspense fallback={fallback || <GlobalSpinner />}>
        <LazyComp />
      </Suspense>
    </ErrorBoundary>
  );
}

// Usage:
function AppWithSafeLazy() {
  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/dashboard"
          element={
            <SafeLazyRoute
              component={LazyDashboard}
              fallback={<SkeletonDashboard />}
              errorFallback={<p>Failed to load dashboard. Please refresh.</p>}
            />
          }
        />
      </Routes>
    </BrowserRouter>
  );
}


// ============================================================
// SECTION 7: REACT 18 — useTransition
// ============================================================

// useTransition marks state updates as NON-URGENT (low priority)
// React can interrupt the transition to handle urgent updates (like typing)
function SearchWithTransition() {
  const [query,   setQuery]   = useState('');
  const [results, setResults] = useState([]);
  const [isPending, startTransition] = useTransition();

  function handleChange(e) {
    const value = e.target.value;
    setQuery(value); // URGENT: update input immediately

    startTransition(() => {
      // LOW-PRIORITY: can be interrupted by urgent updates
      const filtered = expensiveSearch(value);
      setResults(filtered);
    });
  }

  return (
    <div>
      <input value={query} onChange={handleChange} placeholder="Search..." />
      {isPending && <span style={{ color: 'grey' }}> Searching...</span>}
      <ul>
        {results.map(r => <li key={r.id}>{r.name}</li>)}
      </ul>
    </div>
  );
}

function expensiveSearch(query) {
  // Simulate expensive filter
  const data = Array.from({ length: 10000 }, (_, i) => ({ id: i, name: `Item ${i}` }));
  return data.filter(item => item.name.toLowerCase().includes(query.toLowerCase())).slice(0, 20);
}

// startTransition without isPending (when you don't need loading state)
function TabSwitcher() {
  const [tab, setTab] = useState('home');

  function switchTab(newTab) {
    startTransition(() => {
      setTab(newTab); // Low-priority render
    });
  }

  return (
    <div>
      <button onClick={() => switchTab('home')}>Home</button>
      <button onClick={() => switchTab('posts')}>Posts</button>
      <button onClick={() => switchTab('contact')}>Contact</button>
      <TabContent tab={tab} />
    </div>
  );
}

function TabContent({ tab }) {
  // Simulating slow render
  const items = tab === 'posts' ? Array.from({ length: 500 }, (_, i) => `Post ${i}`) : [];
  return (
    <div>
      {tab === 'home'    && <p>Home Content</p>}
      {tab === 'contact' && <p>Contact Content</p>}
      {tab === 'posts'   && items.map((item, i) => <p key={i}>{item}</p>)}
    </div>
  );
}


// ============================================================
// SECTION 8: REACT 18 — useDeferredValue
// ============================================================

// useDeferredValue defers re-rendering of a slow component
// The input stays responsive, the list re-renders in the background
function SearchWithDeferredValue() {
  const [query, setQuery] = useState('');

  // deferredQuery lags behind query — React renders old value first
  // then re-renders with new value when idle
  const deferredQuery = useDeferredValue(query);

  // isStale: true when the UI is showing deferred (old) value
  const isStale = query !== deferredQuery;

  return (
    <div>
      <input
        value={query}
        onChange={e => setQuery(e.target.value)}
        placeholder="Type to search..."
      />
      {/* Memoize so it only re-renders when deferredQuery changes */}
      <div style={{ opacity: isStale ? 0.5 : 1 }}>
        <SlowList query={deferredQuery} />
      </div>
    </div>
  );
}

// React.memo so it only re-renders when query prop changes
const SlowList = React.memo(function SlowList({ query }) {
  const items = Array.from({ length: 5000 }, (_, i) => `Item ${i}`).filter(
    item => item.includes(query)
  );
  return <ul>{items.slice(0, 50).map((item, i) => <li key={i}>{item}</li>)}</ul>;
});

// --- useTransition vs useDeferredValue ---
// useTransition: You control when to mark something as low-priority (wrap setState)
// useDeferredValue: You receive a value and defer its propagation to children
//
// Use useTransition when you own the state update
// Use useDeferredValue when you receive the value as a prop (from parent)


// ============================================================
// SECTION 9: OPTIMISTIC UI with React 18
// ============================================================

// Optimistic update: update UI immediately, rollback on error
function LikeButton({ postId, initialLiked, initialCount }) {
  const [liked,  setLiked]  = useState(initialLiked);
  const [count,  setCount]  = useState(initialCount);
  const [isPending, startTransition] = useTransition();

  async function toggleLike() {
    // 1. Optimistically update UI immediately
    const newLiked = !liked;
    const newCount = newLiked ? count + 1 : count - 1;
    setLiked(newLiked);
    setCount(newCount);

    try {
      // 2. Send to server in background (low priority)
      startTransition(async () => {
        await fetch(`/api/posts/${postId}/like`, {
          method: 'POST',
          body: JSON.stringify({ liked: newLiked }),
          headers: { 'Content-Type': 'application/json' },
        });
      });
    } catch {
      // 3. Rollback on failure
      setLiked(liked);
      setCount(count);
    }
  }

  return (
    <button onClick={toggleLike} disabled={isPending}>
      {liked ? 'Unlike' : 'Like'} ({count})
    </button>
  );
}

// Optimistic list addition with rollback
function TodoListOptimistic() {
  const [todos,   setTodos]   = useState([]);
  const [input,   setInput]   = useState('');
  const [pending, setPending] = useState(false);

  async function addTodo() {
    const text = input.trim();
    if (!text) return;

    const tempId = Date.now(); // temporary ID
    const optimisticTodo = { id: tempId, text, status: 'pending' };

    // 1. Add optimistically with "pending" status
    setTodos(prev => [...prev, optimisticTodo]);
    setInput('');
    setPending(true);

    try {
      // 2. Persist to server
      const saved = await fetch('/api/todos', {
        method: 'POST',
        body: JSON.stringify({ text }),
        headers: { 'Content-Type': 'application/json' },
      }).then(r => r.json());

      // 3. Replace temp with real server response
      setTodos(prev => prev.map(t => t.id === tempId ? { ...saved, status: 'saved' } : t));
    } catch {
      // 4. Remove on failure and restore input
      setTodos(prev => prev.filter(t => t.id !== tempId));
      setInput(text);
    } finally {
      setPending(false);
    }
  }

  return (
    <div>
      <input value={input} onChange={e => setInput(e.target.value)} />
      <button onClick={addTodo} disabled={pending}>Add</button>
      <ul>
        {todos.map(t => (
          <li key={t.id} style={{ opacity: t.status === 'pending' ? 0.6 : 1 }}>
            {t.text} {t.status === 'pending' && '(saving...)'}
          </li>
        ))}
      </ul>
    </div>
  );
}


// ============================================================
// SECTION 10: FULL APP WIRING — All patterns together
// ============================================================

const LazyAdminPanel = lazy(() =>
  new Promise(resolve =>
    setTimeout(() => resolve({ default: AdminPage }), 500)
  )
);

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <ErrorBoundary>
          <Suspense fallback={<GlobalSpinner />}>
            <Routes>
              {/* Public routes */}
              <Route path="/" element={<RootLayout />}>
                <Route index element={<HomePage />} />
                <Route path="about"   element={<AboutPage />} />
                <Route path="login"   element={<LoginPage />} />
                <Route path="unauthorized" element={<UnauthorizedPage />} />

                {/* Blog — nested with params */}
                <Route path="blog" element={<BlogList />} />
                <Route path="blog/:category/:postId" element={<BlogPost />} />

                {/* Protected — any logged-in user */}
                <Route
                  path="dashboard"
                  element={
                    <ProtectedRoute>
                      <DashboardLayout />
                    </ProtectedRoute>
                  }
                >
                  <Route index              element={<DashboardOverview />} />
                  <Route path="settings"   element={<DashboardSettings />} />
                  <Route path="analytics"  element={<DashboardAnalytics />} />
                </Route>

                {/* Protected — admin role required */}
                <Route
                  path="admin"
                  element={
                    <RoleProtectedRoute requiredRole="admin">
                      <Suspense fallback={<p>Loading admin panel...</p>}>
                        <LazyAdminPanel />
                      </Suspense>
                    </RoleProtectedRoute>
                  }
                />

                {/* Redirect example */}
                <Route path="old-path" element={<Navigate to="/about" replace />} />

                {/* 404 catch-all */}
                <Route path="*" element={<NotFoundPage />} />
              </Route>
            </Routes>
          </Suspense>
        </ErrorBoundary>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;

/*
=================================================================
QUICK REFERENCE — React Router v6 + React 18

ROUTING
  <BrowserRouter>          — HTML5 history API router (use at root)
  <Routes>                 — Container for Route definitions
  <Route path="" element>  — Maps URL to component
  <Route index>            — Default child route (no path needed)
  <Navigate to="">         — Declarative redirect
  <Outlet />               — Renders matched child in parent layout
  <Link to="">             — Renders <a>, no page reload
  <NavLink to="">          — Link with isActive state for styling

HOOKS
  useNavigate()            — navigate('/path') or navigate(-1)
  useParams()              — { id, category } from :id, :category
  useSearchParams()        — [params, setParams] for ?key=value
  useLocation()            — { pathname, search, hash, state }

REACT 18 CONCURRENT FEATURES
  useTransition()          — [isPending, startTransition]
                             Mark state updates as low-priority
  useDeferredValue(val)    — Defers re-rendering based on value
  startTransition(fn)      — Standalone (no isPending)

LAZY LOADING
  lazy(() => import('./X')) — Creates lazy component
  <Suspense fallback={...}> — Shows fallback while loading

ERROR HANDLING
  class ErrorBoundary       — Catches errors in render/lifecycle
  getDerivedStateFromError  — Set error state
  componentDidCatch         — Log to error service
=================================================================
*/
