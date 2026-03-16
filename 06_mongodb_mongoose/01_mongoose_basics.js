// ============================================================
// MONGODB + MONGOOSE — Interview Essentials
// ============================================================
// npm install mongoose

const mongoose = require("mongoose");

// ── CONNECT ──────────────────────────────────────────────────
async function connectDB() {
    try {
        await mongoose.connect(process.env.MONGODB_URI || "mongodb://localhost:27017/mydb");
        console.log("MongoDB connected");
    } catch (err) {
        console.error("Connection failed:", err.message);
        process.exit(1);   // exit app if DB fails
    }
}

// ── SCHEMA ─────────────────────────────────────────────────
// Schema = defines the STRUCTURE and VALIDATION of documents
const userSchema = new mongoose.Schema(
    {
        name: {
            type:     String,
            required: [true, "Name is required"],
            trim:     true,            // remove whitespace
            minlength: [2, "Name too short"]
        },
        email: {
            type:     String,
            required: true,
            unique:   true,            // creates a unique index
            lowercase: true,
            match:    [/^\S+@\S+\.\S+$/, "Invalid email format"]
        },
        password: {
            type:     String,
            required: true,
            minlength: 6,
            select:   false           // don't include in query results by default
        },
        role: {
            type:    String,
            enum:    ["user", "admin", "moderator"],   // only these values allowed
            default: "user"
        },
        age: {
            type: Number,
            min:  0,
            max:  150
        },
        isActive: {
            type:    Boolean,
            default: true
        },
        tags: [String],               // array of strings
        address: {                    // nested object
            street: String,
            city:   String,
            country: { type: String, default: "India" }
        }
    },
    {
        timestamps: true    // automatically adds createdAt and updatedAt fields
    }
);

// ── VIRTUAL FIELDS ────────────────────────────────────────────
// Computed properties — not stored in DB
userSchema.virtual("displayName").get(function() {
    return `${this.name} (${this.email})`;
    // use regular function, not arrow — need 'this' context
});

// ── MIDDLEWARE (hooks) ────────────────────────────────────────
// pre("save"): runs BEFORE saving to database
userSchema.pre("save", async function(next) {
    // Only hash password if it was modified
    if (!this.isModified("password")) return next();

    const bcrypt = require("bcryptjs");
    this.password = await bcrypt.hash(this.password, 10);
    next();
});

// post("save"): runs AFTER saving
userSchema.post("save", function(doc) {
    console.log(`User saved: ${doc.email}`);
});

// ── INSTANCE METHODS ──────────────────────────────────────────
// Methods available on each document instance
userSchema.methods.comparePassword = async function(candidatePassword) {
    const bcrypt = require("bcryptjs");
    return bcrypt.compare(candidatePassword, this.password);
};

userSchema.methods.toJSON = function() {
    const obj = this.toObject();
    delete obj.password;   // remove password from JSON output
    return obj;
};

// ── STATIC METHODS ────────────────────────────────────────────
// Methods on the Model (not instances)
userSchema.statics.findByEmail = function(email) {
    return this.findOne({ email: email.toLowerCase() });
};

// ── CREATE MODEL ──────────────────────────────────────────────
// Model = interface to the "users" MongoDB collection
const User = mongoose.model("User", userSchema);


// ── CRUD OPERATIONS ───────────────────────────────────────────

// CREATE
async function createUser() {
    // Method 1: new + save
    const user = new User({ name: "Chaman", email: "c@y.com", password: "pass123" });
    await user.save();   // triggers pre("save") hook

    // Method 2: User.create() — shortcut for new + save
    const user2 = await User.create({ name: "Alice", email: "a@y.com", password: "pass456" });

    return user2;
}

// READ
async function readUsers() {
    // Find all
    const allUsers = await User.find();

    // Find with filter
    const activeUsers = await User.find({ isActive: true });

    // Find with multiple conditions
    const users = await User.find({ isActive: true, age: { $gt: 18 } });

    // Find one
    const user = await User.findOne({ email: "c@y.com" });

    // Find by ID
    const byId = await User.findById("64abc123...");

    // Select specific fields (projection)
    const names = await User.find().select("name email -_id");

    // Sort
    const sorted = await User.find().sort({ createdAt: -1 });  // newest first

    // Limit + skip (pagination)
    const page = 1;
    const limit = 10;
    const paginated = await User.find()
        .skip((page - 1) * limit)
        .limit(limit)
        .sort({ name: 1 });

    return allUsers;
}

// UPDATE
async function updateUser(id) {
    // findByIdAndUpdate returns the UPDATED document with {new: true}
    const updated = await User.findByIdAndUpdate(
        id,
        { $set: { name: "New Name", isActive: false } },  // $set = only update these fields
        { new: true, runValidators: true }                 // options
    );

    // Other update operators:
    // $set     — set fields
    // $push    — add to array: { $push: { tags: "new-tag" } }
    // $pull    — remove from array: { $pull: { tags: "old-tag" } }
    // $inc     — increment: { $inc: { loginCount: 1 } }
    // $unset   — remove field: { $unset: { oldField: "" } }

    return updated;
}

// DELETE
async function deleteUser(id) {
    await User.findByIdAndDelete(id);
    // or: await User.deleteOne({ email: "x@y.com" })
    // or: await User.deleteMany({ isActive: false })
}

// ── RELATIONSHIPS ─────────────────────────────────────────────
const postSchema = new mongoose.Schema({
    title:  { type: String, required: true },
    body:   String,
    author: { type: mongoose.Schema.Types.ObjectId, ref: "User" },  // reference to User
    tags:   [String]
}, { timestamps: true });

const Post = mongoose.model("Post", postSchema);

// Create post with author reference
async function createPost(authorId) {
    const post = await Post.create({
        title:  "My First Post",
        body:   "Hello World",
        author: authorId   // store the User's ObjectId
    });
    return post;
}

// Populate — replace ObjectId with actual document
async function getPostsWithAuthors() {
    const posts = await Post.find()
        .populate("author", "name email")   // populate author, only return name + email
        .sort({ createdAt: -1 });
    return posts;
}

// ── AGGREGATION ───────────────────────────────────────────────
async function aggregationExamples() {
    // Count users per role
    const byRole = await User.aggregate([
        { $match: { isActive: true } },         // filter
        { $group: { _id: "$role", count: { $sum: 1 } } },  // group + count
        { $sort:  { count: -1 } }               // sort by count descending
    ]);

    // $lookup — JOIN with another collection
    const usersWithPosts = await User.aggregate([
        { $match: { isActive: true } },
        {
            $lookup: {
                from:         "posts",     // collection to join
                localField:   "_id",       // field in User
                foreignField: "author",    // field in Post
                as:           "posts"      // output array name
            }
        },
        { $project: { name: 1, email: 1, postCount: { $size: "$posts" } } }
    ]);

    return { byRole, usersWithPosts };
}
