// ============================================================
// TYPESCRIPT + REACT — Interview Essentials
// ============================================================

import React, { useState, useEffect, createContext, useContext } from "react";

// ── TYPED PROPS — Interface for component props ───────────────
interface ButtonProps {
    label:     string;
    onClick:   () => void;
    disabled?: boolean;
    variant?:  "primary" | "secondary" | "danger";
    size?:     "sm" | "md" | "lg";
    children?: React.ReactNode;  // for components that wrap children
}

// Functional component with typed props
const Button: React.FC<ButtonProps> = ({
    label,
    onClick,
    disabled = false,
    variant  = "primary",
    size     = "md",
}) => {
    return (
        <button
            onClick={onClick}
            disabled={disabled}
            className={`btn btn-${variant} btn-${size}`}
        >
            {label}
        </button>
    );
};

// ── TYPED STATE ───────────────────────────────────────────────
interface User {
    id:    number;
    name:  string;
    email: string;
    role:  "admin" | "user" | "moderator";
}

interface FetchState<T> {
    data:    T | null;
    loading: boolean;
    error:   string | null;
}

function useUsers() {
    const [state, setState] = useState<FetchState<User[]>>({
        data:    null,
        loading: false,
        error:   null,
    });

    useEffect(() => {
        setState(prev => ({ ...prev, loading: true }));

        fetch("/api/users")
            .then(res => res.json())
            .then((data: User[]) => setState({ data, loading: false, error: null }))
            .catch((err: Error) => setState({ data: null, loading: false, error: err.message }));
    }, []);

    return state;
}

// ── TYPED CONTEXT ─────────────────────────────────────────────
interface AuthContextType {
    user:   User | null;
    login:  (email: string, password: string) => Promise<void>;
    logout: () => void;
    isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | null>(null);

// Custom hook for consuming context (with type safety)
function useAuth(): AuthContextType {
    const ctx = useContext(AuthContext);
    if (!ctx) throw new Error("useAuth must be used within AuthProvider");
    return ctx;
}

function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<User | null>(null);

    const login = async (email: string, password: string): Promise<void> => {
        const res  = await fetch("/api/auth/login", {
            method:  "POST",
            headers: { "Content-Type": "application/json" },
            body:    JSON.stringify({ email, password }),
        });
        const data = await res.json();
        setUser(data.user);
    };

    const logout = (): void => setUser(null);

    return (
        <AuthContext.Provider value={{ user, login, logout, isAuthenticated: !!user }}>
            {children}
        </AuthContext.Provider>
    );
}

// ── TYPED EVENT HANDLERS ──────────────────────────────────────
function LoginForm() {
    const [email, setEmail]       = useState("");
    const [password, setPassword] = useState("");
    const { login } = useAuth();

    // Typed event — React.ChangeEvent<HTMLInputElement>
    const handleEmailChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
        setEmail(e.target.value);
    };

    // Typed form submit event
    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>): Promise<void> => {
        e.preventDefault();
        await login(email, password);
    };

    return (
        <form onSubmit={handleSubmit}>
            <input type="email" value={email} onChange={handleEmailChange} />
            <input type="password" value={password} onChange={e => setPassword(e.target.value)} />
            <Button label="Login" onClick={() => {}} />
        </form>
    );
}

// ── TYPED API CALL ────────────────────────────────────────────
async function apiCall<T>(url: string, options?: RequestInit): Promise<T> {
    const res = await fetch(url, {
        headers: { "Content-Type": "application/json" },
        ...options,
    });
    if (!res.ok) throw new Error(`API error: ${res.status}`);
    return res.json() as Promise<T>;
}

// Usage
const users = await apiCall<User[]>("/api/users");
const user  = await apiCall<User>("/api/users/1");

// ── GENERIC REUSABLE COMPONENT ────────────────────────────────
interface TableProps<T> {
    data:    T[];
    columns: {
        key:    keyof T;
        header: string;
    }[];
}

function Table<T extends { id: number }>({ data, columns }: TableProps<T>) {
    return (
        <table>
            <thead>
                <tr>{columns.map(col => <th key={String(col.key)}>{col.header}</th>)}</tr>
            </thead>
            <tbody>
                {data.map(row => (
                    <tr key={row.id}>
                        {columns.map(col => (
                            <td key={String(col.key)}>{String(row[col.key])}</td>
                        ))}
                    </tr>
                ))}
            </tbody>
        </table>
    );
}

// Usage
// <Table<User>
//     data={users}
//     columns={[
//         { key: "name",  header: "Name" },
//         { key: "email", header: "Email" },
//     ]}
// />

export { Button, AuthProvider, LoginForm, Table };
