// ============================================================
// REACT INTERMEDIATE HOOKS — Interview Essentials
// ============================================================

import React, {
    useState, useEffect, useContext, useMemo, useCallback,
    createContext, useReducer
} from "react";
import { BrowserRouter, Routes, Route, useNavigate, useParams, Link } from "react-router-dom";

// ── useContext — Share Data Without Prop Drilling ─────────────
// Step 1: Create context
const ThemeContext = createContext("light");
const AuthContext  = createContext(null);

// Step 2: Create provider (wrap your app with this)
function AuthProvider({ children }) {
    const [user, setUser] = useState(null);

    const login = async (email, password) => {
        // Call API, set user
        setUser({ id: 1, email, name: "Chaman" });
    };

    const logout = () => setUser(null);

    return (
        <AuthContext.Provider value={{ user, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
}

// Step 3: Consume anywhere in the tree (no prop drilling)
function Navbar() {
    const { user, logout } = useContext(AuthContext);
    return (
        <nav>
            <span>{user ? `Hello ${user.name}` : "Not logged in"}</span>
            {user && <button onClick={logout}>Logout</button>}
        </nav>
    );
}

// ── useMemo — Cache Expensive Calculations ─────────────────
// Only recalculates when dependencies change
// Use for: expensive transformations, filtered/sorted lists

function FilteredList({ items, searchQuery }) {
    // Without useMemo: filteredItems is recalculated on EVERY render
    // With useMemo: only recalculated when items or searchQuery changes
    const filteredItems = useMemo(() => {
        console.log("Filtering...");   // this should not run too often
        return items.filter(item =>
            item.name.toLowerCase().includes(searchQuery.toLowerCase())
        );
    }, [items, searchQuery]);

    return (
        <ul>
            {filteredItems.map(item => (
                <li key={item.id}>{item.name}</li>
            ))}
        </ul>
    );
}

// ── useCallback — Cache Function References ─────────────────
// Prevents child re-render when passing callbacks as props
// Without useCallback: new function reference on every render → child re-renders
// With useCallback: same reference until deps change → child doesn't re-render

const ItemRow = React.memo(({ item, onDelete }) => {
    console.log(`Rendering ${item.name}`);  // should not run unnecessarily
    return (
        <li>
            {item.name}
            <button onClick={() => onDelete(item.id)}>Delete</button>
        </li>
    );
});

function ItemList({ items, onDeleteItem }) {
    // Cache this function — only recreate when onDeleteItem changes
    const handleDelete = useCallback((id) => {
        console.log(`Deleting ${id}`);
        onDeleteItem(id);
    }, [onDeleteItem]);

    return (
        <ul>
            {items.map(item => (
                <ItemRow key={item.id} item={item} onDelete={handleDelete} />
            ))}
        </ul>
    );
}

// When to use useMemo vs useCallback:
// useMemo    → cache a VALUE (computed result)
// useCallback → cache a FUNCTION (to pass as prop)

// ── React Router ─────────────────────────────────────────────
function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/"          element={<HomePage />} />
                <Route path="/users"     element={<UsersPage />} />
                <Route path="/users/:id" element={<UserDetailPage />} />
                <Route path="*"          element={<NotFoundPage />} />
            </Routes>
        </BrowserRouter>
    );
}

function HomePage() {
    const navigate = useNavigate();   // programmatic navigation

    return (
        <div>
            <h1>Home</h1>
            <Link to="/users">View Users</Link>
            <button onClick={() => navigate("/users")}>Go to Users</button>
            <button onClick={() => navigate(-1)}>Go Back</button>
        </div>
    );
}

function UserDetailPage() {
    const { id } = useParams();   // get :id from URL
    const navigate = useNavigate();

    return (
        <div>
            <h1>User {id}</h1>
            <button onClick={() => navigate("/users")}>Back to list</button>
        </div>
    );
}

function UsersPage() { return <h1>Users</h1>; }
function NotFoundPage() { return <h1>404 Not Found</h1>; }

// ── useReducer — Complex State Management ──────────────────
// Like useState but for complex state with multiple actions
// Good when: multiple related state values, complex update logic

const initialState = { items: [], loading: false, error: null };

function cartReducer(state, action) {
    switch (action.type) {
        case "ADD_ITEM":
            return { ...state, items: [...state.items, action.payload] };
        case "REMOVE_ITEM":
            return { ...state, items: state.items.filter(i => i.id !== action.payload) };
        case "SET_LOADING":
            return { ...state, loading: action.payload };
        case "SET_ERROR":
            return { ...state, error: action.payload };
        case "CLEAR_CART":
            return { ...state, items: [] };
        default:
            return state;
    }
}

function ShoppingCart() {
    const [state, dispatch] = useReducer(cartReducer, initialState);

    const addItem = (item) => dispatch({ type: "ADD_ITEM", payload: item });
    const removeItem = (id) => dispatch({ type: "REMOVE_ITEM", payload: id });

    return (
        <div>
            <p>Items: {state.items.length}</p>
            <button onClick={() => addItem({ id: 1, name: "Book", price: 299 })}>
                Add Book
            </button>
            <button onClick={() => dispatch({ type: "CLEAR_CART" })}>
                Clear
            </button>
        </div>
    );
}

export { AuthProvider, App, ShoppingCart };
