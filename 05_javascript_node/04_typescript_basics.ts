// ============================================================
// TYPESCRIPT BASICS — Interview Essentials
// ============================================================
// TypeScript = JavaScript + static types
// Catches errors at COMPILE TIME before they happen at runtime
// All valid JavaScript is valid TypeScript

// ── BASIC TYPES ───────────────────────────────────────────────
let name: string = "Chaman";
let age: number = 21;
let isActive: boolean = true;
let nothing: null = null;
let notDefined: undefined = undefined;
let anything: any = "use sparingly!";   // opt-out of type checking
let noReturn: void = undefined;         // function returns nothing

// Type inference — TypeScript can often figure out the type
let inferredString = "hello";   // TypeScript infers: string
let inferredNum = 42;           // TypeScript infers: number

// ── INTERFACES ────────────────────────────────────────────────
// Define the shape of an object
interface User {
    id:      number;
    name:    string;
    email:   string;
    role?:   string;   // ? = optional field
    readonly createdAt: Date;  // readonly = can't change after creation
}

const user: User = {
    id: 1,
    name: "Chaman",
    email: "c@y.com",
    createdAt: new Date()
};
// user.createdAt = new Date();  // ERROR: readonly

// Extending interfaces
interface AdminUser extends User {
    permissions: string[];
    adminLevel:  number;
}

// ── TYPE ALIASES ──────────────────────────────────────────────
// More flexible than interfaces — can be unions, primitives, etc.
type Status = "pending" | "active" | "resolved" | "closed";   // union type
type ID = string | number;                                     // union of primitives
type Callback = (err: Error | null, result?: any) => void;

// Use interface for objects/classes, type for unions/primitives
const caseStatus: Status = "pending";
// const badStatus: Status = "open";  // ERROR: "open" is not a valid Status

// ── FUNCTION TYPES ────────────────────────────────────────────
// Type annotations on parameters and return value
function add(a: number, b: number): number {
    return a + b;
}

// Arrow function with types
const multiply = (a: number, b: number): number => a * b;

// Optional and default parameters
function greet(name: string, title: string = "Mr"): string {
    return `Hello ${title}. ${name}`;
}

// Rest parameters
function sum(...numbers: number[]): number {
    return numbers.reduce((acc, n) => acc + n, 0);
}

// ── GENERICS ─────────────────────────────────────────────────
// Functions that work with ANY type — T is a placeholder

// Generic function
function identity<T>(arg: T): T {
    return arg;
}

const strResult = identity<string>("hello");   // T = string
const numResult = identity<number>(42);        // T = number
const inferred  = identity("world");           // TypeScript infers T = string

// Generic array function
function getFirst<T>(arr: T[]): T | undefined {
    return arr[0];
}

// Generic interface
interface ApiResponse<T> {
    data:    T;
    status:  number;
    message: string;
}

const userResponse: ApiResponse<User> = {
    data:    { id: 1, name: "Chaman", email: "c@y.com", createdAt: new Date() },
    status:  200,
    message: "Success"
};

// ── ARRAYS AND TUPLES ─────────────────────────────────────────
const names: string[]  = ["Alice", "Bob"];
const scores: number[] = [90, 85, 92];

// Tuple — fixed-length array with specific types at each position
const point: [number, number] = [10, 20];
const nameAge: [string, number] = ["Chaman", 21];

// ── ENUMS ────────────────────────────────────────────────────
enum CaseStatus {
    Open     = "open",
    InProgress = "in_progress",
    Resolved = "resolved",
    Closed   = "closed"
}

const status: CaseStatus = CaseStatus.Open;

// ── TYPE ASSERTIONS ───────────────────────────────────────────
const element = document.getElementById("myDiv") as HTMLDivElement;
// Tells TS: "I know this is an HTMLDivElement, trust me"

// ── TYPESCRIPT IN EXPRESS ─────────────────────────────────────
// npm install @types/express @types/node

import { Request, Response, NextFunction } from "express";

// Extend Request to add user property
interface AuthRequest extends Request {
    user?: {
        id:    number;
        email: string;
        role?: string;
    };
}

// Typed route handler
const getProfile = (req: AuthRequest, res: Response): void => {
    if (!req.user) {
        res.status(401).json({ error: "Not authenticated" });
        return;
    }
    res.json({ user: req.user });
};

// Typed middleware
const authMiddleware = (req: AuthRequest, res: Response, next: NextFunction): void => {
    // verify JWT, attach req.user
    req.user = { id: 1, email: "c@y.com" };
    next();
};

// ── TYPESCRIPT IN REACT ───────────────────────────────────────
// Define props interface for components
interface ButtonProps {
    label:     string;
    onClick:   () => void;
    disabled?: boolean;
    variant?:  "primary" | "secondary" | "danger";
}

// Typed functional component
// const Button: React.FC<ButtonProps> = ({ label, onClick, disabled = false }) => (
//     <button onClick={onClick} disabled={disabled}>{label}</button>
// );

// Typed useState
// const [users, setUsers] = useState<User[]>([]);
// const [loading, setLoading] = useState<boolean>(false);
// const [error, setError] = useState<string | null>(null);
