// ============================================================
// JAVASCRIPT / NODE.JS BASICS — Interview Essentials
// ============================================================

// ── VARIABLES ────────────────────────────────────────────────
// const: can't reassign → use by default
// let:   can reassign → use when you need to change the value
// var:   function-scoped, hoisted → NEVER USE in modern JS

const name = "Chaman";
let count = 0;
count = 1;   // OK with let
// name = "x"; // ERROR — const can't be reassigned

// ── ARROW FUNCTIONS ──────────────────────────────────────────
// Regular function
function add(a, b) {
    return a + b;
}

// Arrow function (modern, cleaner)
const addArrow = (a, b) => a + b;   // implicit return for single expression

const greet = name => `Hello ${name}`;   // single param — no parentheses needed

const doSomething = () => {
    // multiple lines need curly braces and explicit return
    const result = 42;
    return result;
};

// ── TEMPLATE LITERALS ────────────────────────────────────────
const age = 21;
const message = `Hi, I'm ${name} and I'm ${age} years old`;   // backtick!
const multiLine = `
    This is
    a multi-line
    string
`;

// ── DESTRUCTURING ─────────────────────────────────────────────
const user = { id: 1, name: "Chaman", email: "c@y.com", city: "Bangalore" };
const { name: userName, email, city = "Unknown" } = user;   // city has default
console.log(userName, email, city);

const arr = [1, 2, 3, 4, 5];
const [first, second, ...rest] = arr;
console.log(first, second, rest);   // 1 2 [3,4,5]

// In function parameters
function displayUser({ name, email }) {
    console.log(`${name}: ${email}`);
}
displayUser(user);

// ── SPREAD OPERATOR ───────────────────────────────────────────
// Arrays
const nums = [1, 2, 3];
const newNums = [...nums, 4, 5];        // [1, 2, 3, 4, 5]
const copiedNums = [...nums];           // shallow copy

// Objects
const settings = { theme: "dark", lang: "en" };
const newSettings = { ...settings, lang: "hi", fontSize: 14 };  // override lang
// { theme: "dark", lang: "hi", fontSize: 14 }

// ── PROMISES ─────────────────────────────────────────────────
// A Promise represents a future value — it either resolves or rejects

const fetchUser = (id) => {
    return new Promise((resolve, reject) => {
        // Simulate async work
        setTimeout(() => {
            if (id > 0) {
                resolve({ id, name: "Chaman" });   // success
            } else {
                reject(new Error("Invalid ID"));   // failure
            }
        }, 100);
    });
};

// Using .then() / .catch()
fetchUser(1)
    .then(user => console.log("User:", user))
    .catch(err => console.error("Error:", err.message))
    .finally(() => console.log("Request finished"));   // always runs

// ── ASYNC/AWAIT ────────────────────────────────────────────
// Cleaner way to write Promises — looks like synchronous code

async function getUser(id) {
    try {
        const user = await fetchUser(id);   // wait for promise to resolve
        console.log("Got user:", user);
        return user;
    } catch (err) {
        console.error("Failed:", err.message);
        throw err;   // re-throw if you want caller to handle it
    }
}

// Can also use arrow functions
const getUserArrow = async (id) => {
    const user = await fetchUser(id);
    return user;
};

// await only works inside async functions
// Multiple awaits in parallel — use Promise.all
async function fetchMultiple() {
    const [user1, user2] = await Promise.all([
        fetchUser(1),
        fetchUser(2)
    ]);
    console.log(user1, user2);
}

// ── ARRAY METHODS ─────────────────────────────────────────────
const numbers = [1, 2, 3, 4, 5];

// map — transform every item
const doubled = numbers.map(n => n * 2);          // [2, 4, 6, 8, 10]

// filter — keep items where callback returns true
const evens = numbers.filter(n => n % 2 === 0);   // [2, 4]

// reduce — fold array into single value
const sum = numbers.reduce((acc, n) => acc + n, 0);  // 15

// find — first item matching condition
const found = numbers.find(n => n > 3);            // 4

// some — true if ANY item matches
const hasEven = numbers.some(n => n % 2 === 0);    // true

// every — true if ALL items match
const allPositive = numbers.every(n => n > 0);     // true

// forEach — like for loop (no return value)
numbers.forEach((n, i) => console.log(i, n));

// ── OPTIONAL CHAINING & NULLISH COALESCING ───────────────────
const profile = { user: { address: { city: "Bangalore" } } };

// Without ?.  you'd get: TypeError: Cannot read property of undefined
const city = profile?.user?.address?.city;          // "Bangalore"
const zip  = profile?.user?.address?.zip;           // undefined (not an error)

// ?? — nullish coalescing: use right side only if left is null or undefined
const displayCity = city ?? "City not available";  // "Bangalore"
const displayZip  = zip  ?? "ZIP not available";   // "ZIP not available"

// ── MODULES ──────────────────────────────────────────────────
// CommonJS (old, still used in Node.js)
// const express = require("express")
// module.exports = { myFunction }

// ES Modules (modern)
// import express from "express"
// export const myFunction = () => {}
// export default MyClass

// ── NODE.JS SPECIFICS ─────────────────────────────────────────
// Node.js = JavaScript that runs on the server (not in a browser)
// - Has access to file system, network, processes
// - No DOM, window, document (browser APIs don't exist here)
// - Built on Chrome's V8 engine
// - Non-blocking, event-driven architecture

// Process and environment
// process.env.PORT            → environment variable
// process.env.NODE_ENV        → "development" or "production"
// process.argv                → command line arguments

// Built-in modules (no install needed)
// const fs   = require("fs")     → file system
// const path = require("path")   → path manipulation
// const http = require("http")   → HTTP server
