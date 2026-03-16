// ============================================================
// REACT PATTERNS — Common Design Patterns for Interviews
// ============================================================
import React, { useState, useEffect, createContext, useContext } from "react";

// ── 1. CONTROLLED FORM ────────────────────────────────────────
// All form values live in React state — single source of truth
function ControlledForm({ onSubmit }) {
    const [form, setForm] = useState({
        name:     "",
        email:    "",
        password: ""
    });
    const [errors, setErrors] = useState({});
    const [submitting, setSubmitting] = useState(false);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setForm(prev => ({ ...prev, [name]: value }));
        if (errors[name]) setErrors(prev => ({ ...prev, [name]: "" }));
    };

    const validate = () => {
        const errs = {};
        if (!form.name)           errs.name = "Name required";
        if (!form.email.includes("@")) errs.email = "Valid email required";
        if (form.password.length < 8)  errs.password = "Min 8 characters";
        return errs;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        const errs = validate();
        if (Object.keys(errs).length > 0) return setErrors(errs);
        setSubmitting(true);
        try {
            await onSubmit(form);
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <form onSubmit={handleSubmit}>
            <input name="name"     value={form.name}     onChange={handleChange} />
            {errors.name && <span className="error">{errors.name}</span>}

            <input name="email"    value={form.email}    onChange={handleChange} />
            {errors.email && <span className="error">{errors.email}</span>}

            <input name="password" type="password" value={form.password} onChange={handleChange} />
            {errors.password && <span className="error">{errors.password}</span>}

            <button type="submit" disabled={submitting}>
                {submitting ? "Submitting..." : "Submit"}
            </button>
        </form>
    );
}


// ── 2. RENDER PROPS PATTERN ───────────────────────────────────
// Share stateful logic by passing a render function as a prop
function DataFetcher({ url, render }) {
    const [data, setData]     = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError]   = useState(null);

    useEffect(() => {
        fetch(url)
            .then(r => r.json())
            .then(setData)
            .catch(setError)
            .finally(() => setLoading(false));
    }, [url]);

    return render({ data, loading, error });
}

// Usage:
// <DataFetcher
//     url="/api/users"
//     render={({ data, loading, error }) => {
//         if (loading) return <Spinner />;
//         if (error) return <Error message={error} />;
//         return <UserList users={data} />;
//     }}
// />


// ── 3. COMPOUND COMPONENT PATTERN ────────────────────────────
// Parent and child components share state implicitly via Context
// Great for flexible UI libraries (Tabs, Accordion, Select)

const TabContext = createContext(null);

function Tabs({ children, defaultTab = 0 }) {
    const [active, setActive] = useState(defaultTab);
    return (
        <TabContext.Provider value={{ active, setActive }}>
            <div className="tabs">{children}</div>
        </TabContext.Provider>
    );
}

function TabList({ children }) {
    return <div className="tab-list">{children}</div>;
}

function Tab({ index, children }) {
    const { active, setActive } = useContext(TabContext);
    return (
        <button
            className={active === index ? "tab active" : "tab"}
            onClick={() => setActive(index)}
        >
            {children}
        </button>
    );
}

function TabPanel({ index, children }) {
    const { active } = useContext(TabContext);
    if (active !== index) return null;
    return <div className="tab-panel">{children}</div>;
}

// Usage — clean, flexible API:
// <Tabs defaultTab={0}>
//     <TabList>
//         <Tab index={0}>Overview</Tab>
//         <Tab index={1}>Details</Tab>
//     </TabList>
//     <TabPanel index={0}><Overview /></TabPanel>
//     <TabPanel index={1}><Details /></TabPanel>
// </Tabs>


// ── 4. ERROR BOUNDARY ─────────────────────────────────────────
// Class component only — catches JS errors in the component tree
// Prevents entire app from crashing on a component error
class ErrorBoundary extends React.Component {
    state = { hasError: false, error: null };

    static getDerivedStateFromError(error) {
        return { hasError: true, error };
    }

    componentDidCatch(error, info) {
        console.error("Error caught:", error, info.componentStack);
        // Log to Sentry: Sentry.captureException(error)
    }

    render() {
        if (this.state.hasError) {
            return (
                <div>
                    <h2>Something went wrong</h2>
                    <button onClick={() => this.setState({ hasError: false })}>
                        Try again
                    </button>
                </div>
            );
        }
        return this.props.children;
    }
}

// Usage:
// <ErrorBoundary>
//     <SomeComponent />  ← if this crashes, ErrorBoundary shows fallback
// </ErrorBoundary>


// ── 5. OPTIMISTIC UI PATTERN ─────────────────────────────────
// Update UI immediately, then sync with server. Roll back on error.
// Makes the app feel instant even with slow networks.

function TodoList() {
    const [todos, setTodos] = useState([]);

    const deleteTodo = async (id) => {
        // Optimistic: remove from UI immediately
        const backup = todos;
        setTodos(todos.filter(t => t.id !== id));

        try {
            await fetch(`/api/todos/${id}`, { method: "DELETE" });
            // Success — UI already updated
        } catch (error) {
            // Rollback on error
            setTodos(backup);
            alert("Delete failed, please try again");
        }
    };

    return (
        <ul>
            {todos.map(todo => (
                <li key={todo.id}>
                    {todo.text}
                    <button onClick={() => deleteTodo(todo.id)}>Delete</button>
                </li>
            ))}
        </ul>
    );
}


// ── 6. LOADING / ERROR / EMPTY STATES ────────────────────────
// Always handle all 4 states: loading, error, empty, data
function CaseList({ clientId }) {
    const [cases, setCases]   = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError]   = useState(null);

    useEffect(() => {
        setLoading(true);
        setError(null);
        fetch(`/api/cases?clientId=${clientId}`)
            .then(r => r.json())
            .then(setCases)
            .catch(e => setError(e.message))
            .finally(() => setLoading(false));
    }, [clientId]);

    if (loading) return <div className="spinner">Loading cases...</div>;
    if (error)   return <div className="error">Error: {error} <button onClick={() => setClientId(clientId)}>Retry</button></div>;
    if (cases.length === 0) return <div className="empty">No cases found</div>;

    return (
        <ul>
            {cases.map(c => <li key={c.id}>{c.title} — {c.status}</li>)}
        </ul>
    );
}


// ── 7. INFINITE SCROLL ───────────────────────────────────────
function InfiniteList() {
    const [items, setItems]     = useState([]);
    const [page, setPage]       = useState(1);
    const [hasMore, setHasMore] = useState(true);
    const [loading, setLoading] = useState(false);
    const loaderRef = React.useRef(null);

    useEffect(() => {
        const observer = new IntersectionObserver(entries => {
            if (entries[0].isIntersecting && hasMore && !loading) {
                setPage(p => p + 1);   // load next page when bottom visible
            }
        });
        if (loaderRef.current) observer.observe(loaderRef.current);
        return () => observer.disconnect();
    }, [hasMore, loading]);

    useEffect(() => {
        if (!hasMore) return;
        setLoading(true);
        fetch(`/api/items?page=${page}&limit=20`)
            .then(r => r.json())
            .then(data => {
                setItems(prev => [...prev, ...data.items]);
                if (!data.hasMore) setHasMore(false);
            })
            .finally(() => setLoading(false));
    }, [page]);

    return (
        <div>
            <ul>{items.map(i => <li key={i.id}>{i.name}</li>)}</ul>
            <div ref={loaderRef}>
                {loading && <p>Loading more...</p>}
                {!hasMore && <p>No more items</p>}
            </div>
        </div>
    );
}

export { ControlledForm, DataFetcher, Tabs, ErrorBoundary, TodoList, CaseList };
