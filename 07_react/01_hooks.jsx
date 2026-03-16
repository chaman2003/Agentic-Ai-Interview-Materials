// ============================================================
// REACT HOOKS — Interview Essentials
// ============================================================

import React, { useState, useEffect, useRef } from "react";

// ── useState ─────────────────────────────────────────────────
// The most basic hook — adds state to a functional component
// const [value, setter] = useState(initialValue)
// NEVER mutate state directly — always use the setter

function Counter() {
    const [count, setCount] = useState(0);  // initial value = 0

    return (
        <div>
            <p>Count: {count}</p>
            <button onClick={() => setCount(count + 1)}>+</button>
            <button onClick={() => setCount(count - 1)}>-</button>
            <button onClick={() => setCount(0)}>Reset</button>
        </div>
    );
}

// State with objects — always spread to preserve other fields
function UserForm() {
    const [user, setUser] = useState({ name: "", email: "" });

    const handleChange = (field) => (e) => {
        setUser({ ...user, [field]: e.target.value });  // spread old state
    };

    return (
        <form>
            <input value={user.name}  onChange={handleChange("name")}  />
            <input value={user.email} onChange={handleChange("email")} />
        </form>
    );
}

// ── useEffect ─────────────────────────────────────────────────
// Run side effects: API calls, subscriptions, timers, DOM manipulation
// Runs AFTER the component renders

function UserProfile({ userId }) {
    const [user, setUser]     = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError]   = useState(null);

    // Dependency array rules:
    // []         — run ONCE on mount (component appears on screen)
    // [userId]   — run whenever userId changes
    // no array   — run after EVERY render (rarely what you want)

    useEffect(() => {
        let cancelled = false;   // prevent state update on unmounted component

        async function fetchUser() {
            try {
                setLoading(true);
                const res  = await fetch(`/api/users/${userId}`);
                const data = await res.json();
                if (!cancelled) {
                    setUser(data);
                }
            } catch (err) {
                if (!cancelled) setError(err.message);
            } finally {
                if (!cancelled) setLoading(false);
            }
        }

        fetchUser();

        // Cleanup function — runs when component unmounts OR before next effect
        return () => { cancelled = true; };
    }, [userId]);  // re-run whenever userId changes

    if (loading) return <p>Loading...</p>;
    if (error)   return <p>Error: {error}</p>;
    if (!user)   return null;

    return <div>{user.name}</div>;
}

// useEffect for event listeners (with cleanup)
function WindowWidth() {
    const [width, setWidth] = useState(window.innerWidth);

    useEffect(() => {
        const handler = () => setWidth(window.innerWidth);
        window.addEventListener("resize", handler);

        // CLEANUP — remove listener when component unmounts
        return () => window.removeEventListener("resize", handler);
    }, []);  // [] = setup once, cleanup once

    return <p>Window width: {width}px</p>;
}

// ── useRef ────────────────────────────────────────────────────
// 1. Reference a DOM element directly
// 2. Persist a value across renders WITHOUT causing re-render

function FocusInput() {
    const inputRef = useRef(null);   // initially null

    const focusInput = () => {
        inputRef.current.focus();    // directly call DOM method
    };

    return (
        <div>
            <input ref={inputRef} placeholder="I'll get focused" />
            <button onClick={focusInput}>Focus Input</button>
        </div>
    );
}

// useRef to store value without re-render (e.g., previous value)
function TimerComponent() {
    const [count, setCount] = useState(0);
    const intervalRef = useRef(null);   // store timer ID

    const start = () => {
        intervalRef.current = setInterval(() => {
            setCount(c => c + 1);
        }, 1000);
    };

    const stop = () => {
        clearInterval(intervalRef.current);  // access stored timer ID
    };

    return (
        <div>
            <p>Count: {count}</p>
            <button onClick={start}>Start</button>
            <button onClick={stop}>Stop</button>
        </div>
    );
}

export { Counter, UserProfile, FocusInput };
