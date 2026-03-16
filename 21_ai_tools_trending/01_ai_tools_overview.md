# AI TOOLS, MCP, CLI, IDE & TRENDING TECH — COMPREHENSIVE GUIDE

## TABLE OF CONTENTS
1. [AI Code Assistants & IDEs](#ai-code-assistants--ides)
2. [Model Context Protocol (MCP)](#model-context-protocol-mcp)
3. [CLI Tools & Terminal Workflows](#cli-tools--terminal-workflows)
4. [Hooks, Skills & Instructions](#hooks-skills--instructions)
5. [Trending AI Tools & Frameworks](#trending-ai-tools--frameworks)
6. [Tips, Tricks & Best Practices](#tips-tricks--best-practices)
7. [Interview Questions](#interview-questions)

---

## AI CODE ASSISTANTS & IDEs

### 🤖 GitHub Copilot
**What it is**: AI pair programmer by GitHub (powered by OpenAI Codex)

**Features**:
- ✅ Inline code suggestions as you type
- ✅ Multi-line completions
- ✅ Context-aware from entire file
- ✅ Support for 10+ languages
- ✅ Comment-to-code generation

**How to use**:
```javascript
// Example: Just write a comment, Copilot suggests implementation
// Function to fetch user data from API and cache in Redis
async function getUserData(userId) {
  // Copilot autocompletes:
  const cacheKey = `user:${userId}`;
  let user = await redis.get(cacheKey);

  if (!user) {
    user = await fetch(`/api/users/${userId}`).then(r => r.json());
    await redis.setex(cacheKey, 3600, JSON.stringify(user));
  }

  return JSON.parse(user);
}
```

**Tips**:
- Write clear comments describing what you want
- Use descriptive function/variable names
- Copilot learns from your codebase patterns
- Press `Tab` to accept, `Esc` to reject suggestion

**Pricing**: $10/month for individuals, $19/month for business

---

### 🖥️ Cursor IDE
**What it is**: VS Code fork with built-in AI (GPT-4)

**Features**:
- ✅ Chat with your codebase (Cmd+K / Ctrl+K)
- ✅ Edit code with AI (Cmd+L / Ctrl+L)
- ✅ Inline generation (Cmd+Shift+K)
- ✅ Codebase-wide search & understand
- ✅ Terminal integration

**Use cases**:
1. **Ask about code**: "What does this function do?"
2. **Refactor**: "Convert this to TypeScript"
3. **Debug**: "Why is this throwing an error?"
4. **Generate tests**: "Write unit tests for this component"
5. **Explain**: "Explain this regex pattern"

**Example workflow**:
```bash
# 1. Select code you don't understand
# 2. Press Cmd+K
# 3. Ask: "Explain what this code does"
# AI explains the selected code in plain English

# Edit existing code
# 1. Select code
# 2. Press Cmd+L
# 3. Type: "Add error handling and logging"
# AI edits the code in place
```

**vs GitHub Copilot**:
- Copilot: Inline autocomplete (faster, less intrusive)
- Cursor: Chat interface (better for complex tasks, explanations)
- Best: Use both! Cursor for exploration, Copilot for writing

**Pricing**: Free tier available, Pro $20/month

---

### Claude Code (by Anthropic)
**What it is**: Agentic AI coding assistant built directly into the terminal / VS Code. Powered by Claude (Sonnet/Opus).

**Features**:
- Full codebase understanding (reads files, runs commands, edits code)
- Agentic: breaks down tasks, plans, executes multi-step changes autonomously
- Runs in your terminal — no IDE required
- Can run tests, fix failing tests, commit code
- Supports CLAUDE.md project instructions
- MCP tool integrations (databases, APIs, custom tools)

**Unique Capabilities**:
```bash
# Claude Code in action
> Add authentication to this Express app with JWT, write tests, and commit

# Claude Code will:
# 1. Read the entire codebase
# 2. Plan the changes
# 3. Create/edit files
# 4. Run tests
# 5. Fix any failures
# 6. Commit with meaningful message
```

**CLAUDE.md** — Project instruction file:
```markdown
# My Project Instructions

## Tech Stack
- Node.js + Express
- MongoDB
- Jest for testing

## Rules
- Always use async/await
- Error handling required in every route
- No console.log in production code
```

**Pricing**: Pay-per-token via Anthropic API, or via Claude Pro/Teams subscription

---

### Windsurf (by Codeium)
**What it is**: AI-first IDE (VS Code fork) with "Flows" — deeply integrated AI that understands your full coding context

**Features**:
- Cascade: AI agent that plans and executes multi-file changes
- Real-time collaboration with AI across the entire session
- Supercomplete: smarter than autocomplete, understands context
- Terminal integration, test running, debugging
- Free tier available

**Windsurf vs Cursor**:
- Windsurf: Stronger autonomous multi-file edits ("Cascade"), better context retention
- Cursor: Better chat interface, more keyboard shortcuts, larger user base

---

### Lovable.dev (formerly GPT Engineer)
**What it is**: AI-powered full-stack app builder — describe what you want, get a working React + Supabase app

**What it does**:
```
User: "Build a todo app with user auth, categories, and drag-to-reorder"
Lovable: Generates → React frontend + Supabase backend + auth + deployment
```

**Features**:
- Full-stack generation (React + Tailwind + Supabase)
- GitHub sync — push generated code to your repo
- Edit in natural language ("make the button red", "add a search bar")
- One-click deployment
- Great for MVPs and prototypes

**Pricing**: Free tier, then $20/month+

---

### Bolt.new (by StackBlitz)
**What it is**: In-browser AI app builder that generates and runs full-stack apps instantly

**Features**:
- Generates complete apps (React/Vue/Node/Python) from prompts
- Runs the app live in browser (WebContainers)
- Edit via chat or manually
- Export to GitHub or deploy to Netlify
- Zero setup — works instantly in browser

---

### Replit Agent
**What it is**: AI agent inside Replit that builds complete apps autonomously

**Workflow**:
1. Describe what you want in natural language
2. Agent plans the architecture
3. Agent writes all code (frontend + backend + database)
4. Runs and tests the app
5. Deploys automatically

---

### v0 (by Vercel)
**What it is**: AI UI generator — describe a component, get production React + Tailwind code

```
Prompt: "Create a pricing table with 3 tiers, monthly/yearly toggle, and a highlight on the Pro tier"
→ Generates: Clean React component with shadcn/ui and Tailwind
```

---

### Devin AI (by Cognition)
**What it is**: The first "AI software engineer" — autonomous agent that handles full development tasks

**Capabilities**:
- Plans complex multi-step engineering tasks
- Writes code across multiple files
- Runs tests, debugs failures
- Deploys to production
- Commits to GitHub

---

### Zed Editor
**What it is**: Blazing-fast collaborative code editor (Rust-built), with integrated AI

**Features**:
- Native Rust performance (no Electron)
- Built-in real-time collaboration
- AI completions via Claude, Copilot
- Vim mode built-in

---

### JetBrains AI Assistant
**What it is**: AI integrated into all JetBrains IDEs (IntelliJ, PyCharm, WebStorm, etc.)

**Features**:
- Context-aware completions in JetBrains IDEs
- Understands project structure (Maven, Gradle, etc.)
- Code review, explain code, generate tests

---

### Amazon Q Developer (formerly CodeWhisperer)
**What it is**: Amazon's AI coding assistant with deep AWS integration

**Features**:
- Security vulnerability scanning
- AWS service suggestions
- Free for individual use
- Agent mode for multi-file edits

---

### Other Tools

**Tabnine**
- Privacy-focused AI assistant (can run locally on-premise)
- Supports team training on private codebase
- Good for enterprises with strict data security

**Codeium**
- Free forever (even for commercial use)
- 70+ languages, works in any IDE

**Comparison Table**:
| Tool | Price | Category | Best For |
|------|-------|----------|----------|
| GitHub Copilot | $10/mo | IDE extension | Inline autocomplete everywhere |
| Cursor | $20/mo | AI IDE | Chat + codebase exploration |
| Claude Code | Per token | CLI/terminal agent | Autonomous multi-step tasks |
| Windsurf | Free/$15mo | AI IDE | Multi-file autonomous changes |
| Lovable.dev | Free/$20mo | App builder | Full-stack MVP generation |
| Bolt.new | Free/$20mo | App builder | In-browser rapid prototyping |
| v0 by Vercel | Free | UI generator | React component generation |
| Devin AI | ~$500/mo | AI engineer | Complex autonomous engineering |
| Codeium | Free | IDE extension | Budget-friendly Copilot alternative |
| Tabnine | $12/mo | IDE extension | Privacy-first enterprise |
| Amazon Q | Free/$19mo | IDE extension | AWS-specific development |
| Zed | Free | IDE | Fast native editor with AI |

---

## MODEL CONTEXT PROTOCOL (MCP)

### 📡 What is MCP?

**Definition**: Standard protocol for connecting AI assistants with data sources and tools

Think of MCP as:
- 🔌 **USB for AI**: Universal connector between LLMs and external systems
- 🧩 **Plugin system**: Extend AI capabilities with custom tools
- 🌉 **Bridge**: Connect AI to databases, APIs, files, etc.

**Created by**: Anthropic (makers of Claude)

**Why MCP matters**:
- ❌ Before: Each AI tool had custom integrations (messy!)
- ✅ After: One standard protocol for all tools (clean!)

---

### 🏗️ MCP Architecture

```
┌─────────────┐
│   LLM       │  (Claude, GPT, etc.)
│  (Client)   │
└──────┬──────┘
       │ MCP Protocol
       │ (JSON-RPC)
       │
┌──────┴──────┐
│ MCP Server  │  (Your custom tool)
└──────┬──────┘
       │
       ├─── Database (PostgreSQL, MongoDB)
       ├─── API (REST, GraphQL)
       ├─── File System
       └─── External Services (Email, Slack, etc.)
```

**Components**:
1. **MCP Client**: AI assistant (Claude, GPT)
2. **MCP Server**: Your tool/integration
3. **Protocol**: JSON-RPC over stdio/HTTP

---

### 🛠️ Building an MCP Server

**Example: Database Query Tool**

```python
# mcp_server.py — PostgreSQL query tool for Claude
from mcp.server import MCPServer
from mcp.types import Tool, TextContent
import psycopg2

# Initialize MCP server
server = MCPServer("database-tools")

# Define tool
@server.tool()
async def query_database(query: str) -> str:
    """Execute SQL query on PostgreSQL database"""

    # Input validation
    if not query.strip().upper().startswith('SELECT'):
        return "Error: Only SELECT queries allowed"

    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()

        return f"Query executed successfully. Results:\n{results}"
    except Exception as e:
        return f"Error executing query: {str(e)}"
    finally:
        cursor.close()
        conn.close()

# Run server
if __name__ == "__main__":
    server.run()
```

**Using the MCP Server with Claude**:
```json
// claude_desktop_config.json
{
  "mcpServers": {
    "database-tools": {
      "command": "python",
      "args": ["mcp_server.py"],
      "env": {
        "DATABASE_URL": "postgresql://user:pass@localhost/mydb"
      }
    }
  }
}
```

**Now Claude can**:
- Query your database
- Answer questions about your data
- Generate reports from real data

---

### 📦 MCP Concepts

**1. Tools**
Functions that LLM can call

```javascript
// Example tool: Send email
{
  "name": "send_email",
  "description": "Send an email to a recipient",
  "input_schema": {
    "type": "object",
    "properties": {
      "to": { "type": "string", "description": "Email address" },
      "subject": { "type": "string" },
      "body": { "type": "string" }
    },
    "required": ["to", "subject", "body"]
  }
}
```

**2. Resources**
Data that LLM can read (files, databases, APIs)

```javascript
// Example resource: Project README
{
  "uri": "file:///project/README.md",
  "name": "Project README",
  "description": "Documentation for this project",
  "mimeType": "text/markdown"
}
```

**3. Prompts**
Pre-defined prompt templates

```javascript
// Example prompt: Code review
{
  "name": "code_review",
  "description": "Review code for bugs and improvements",
  "arguments": [
    { "name": "code", "required": true }
  ]
}
```

---

### 🌟 MCP Use Cases

1. **Database Access**
   - Let AI query your database
   - Generate reports, dashboards
   - Natural language to SQL

2. **API Integrations**
   - Connect AI to Salesforce, HubSpot, Stripe
   - Automate workflows
   - Retrieve real-time data

3. **File System Access**
   - Read/write files
   - Code generation in projects
   - Documentation updates

4. **Custom Tools**
   - Email automation
   - Slack/Discord bots
   - Payment processing

---

## CLI TOOLS & TERMINAL WORKFLOWS

### 💻 Essential CLI Tools for Developers

**1. `gh` — GitHub CLI**
```bash
# Create pull request
gh pr create --title "Fix bug" --body "Description"

# View PR
gh pr view 123

# Check CI status
gh pr checks

# Merge PR
gh pr merge 123 --squash
```

**2. `jq` — JSON processor**
```bash
# Pretty print JSON
curl https://api.github.com/users/octocat | jq

# Extract specific field
cat data.json | jq '.users[0].name'

# Filter array
cat users.json | jq '.[] | select(.age > 18)'
```

**3. `fzf` — Fuzzy finder**
```bash
# Find file quickly
vim $(fzf)

# Search command history
history | fzf | sh

# Kill process by name
ps aux | fzf | awk '{print $2}' | xargs kill
```

**4. `httpie` — User-friendly HTTP client**
```bash
# GET request
http GET https://api.example.com/users

# POST request with JSON
http POST https://api.example.com/users name="Alice" email="alice@example.com"

# With authentication
http GET https://api.example.com/profile Authorization:"Bearer token123"
```

**5. `tldr` — Simplified man pages**
```bash
# Instead of man curl (too verbose)
tldr curl

# Quick examples for any command
tldr git commit
```

**6. `bat` — Better `cat`**
```bash
# Syntax highlighting, line numbers, git integration
bat server.js

# View diff
bat -d main.js feature.js
```

**7. `ripgrep (rg)` — Faster grep**
```bash
# Search for pattern in all files
rg "function.*async" --type js

# Search and replace
rg "old_name" -l | xargs sed -i 's/old_name/new_name/g'
```

**8. `zoxide` — Smarter cd**
```bash
# Jump to frequently used directories
z projects  # Goes to ~/dev/projects

z doc  # Goes to ~/Documents

# Works from anywhere!
```

---

### 🔧 AI-Powered CLI Tools

**1. `aider` — AI coding assistant in terminal**
```bash
# Install
pip install aider-chat

# Use with GPT-4
aider --model gpt-4 server.js

# Chat and edit files
> Add error handling to the login function

# Commits changes automatically with AI-generated commit messages
```

**2. `warp` — AI-powered terminal**
- Natural language to command: "list all running docker containers"
- AI autocomplete for commands
- Command history search with AI
- Built-in documentation

**3. `GitHub Copilot CLI`**
```bash
# Ask for commands
gh copilot suggest "remove all .log files older than 7 days"

# Explain a command
gh copilot explain "tar -xzvf archive.tar.gz"
```

---

## HOOKS, SKILLS & INSTRUCTIONS

### 🪝 Git Hooks
**What**: Scripts that run automatically on git events

**Common hooks**:
```bash
# .git/hooks/pre-commit — Run before commit
#!/bin/bash
echo "Running tests before commit..."
npm test

if [ $? -ne 0 ]; then
  echo "Tests failed! Commit aborted."
  exit 1
fi

echo "Tests passed! Proceeding with commit."
```

```bash
# .git/hooks/pre-push — Run before push
#!/bin/bash
echo "Running linter before push..."
npm run lint

if [ $? -ne 0 ]; then
  echo "Linting failed! Push aborted."
  exit 1
fi
```

**Use `husky` for easier hook management**:
```bash
# Install
npm install husky --save-dev

# Initialize
npx husky install

# Add hook
npx husky add .husky/pre-commit "npm test"
```

**`lint-staged` for partial commits**:
```json
// package.json
{
  "lint-staged": {
    "*.js": ["eslint --fix", "prettier --write"],
    "*.css": ["stylelint --fix", "prettier --write"]
  }
}
```

---

### 🧠 AI Skills & Instructions

**What**: Configuration files that instruct AI assistants how to behave

**Example: `.cursorrules` (for Cursor IDE)**
```
# Project-specific AI instructions

## Tech Stack
- Backend: Node.js + Express
- Database: MongoDB + Redis
- Frontend: React + TypeScript

## Coding Standards
- Use async/await, not callbacks
- Always include error handling
- Write JSDoc comments for functions
- Use functional components with hooks
- Follow RESTful API conventions

## File Structure
- /api - API routes
- /models - Mongoose models
- /middleware - Express middleware
- /utils - Helper functions

## When writing code:
1. Add input validation
2. Include error messages
3. Log important events
4. Write clean, self-documenting code
5. Prefer composition over inheritance
```

**Example: `.github/copilot-instructions.md`**
```markdown
# GitHub Copilot Instructions

## Code Style
- Use ES6+ features
- Prefer const over let, avoid var
- Use template literals for strings
- Add TypeScript types for public APIs

## Security
- Validate all user input
- Never commit secrets (use .env)
- Use parameterized queries (prevent SQL injection)
- Sanitize HTML to prevent XSS

## Testing
- Write tests for all business logic
- Use meaningful test descriptions
- Mock external dependencies
```

**Example: Claude Desktop Instructions**
```json
// ~/Library/Application Support/Claude/instructions.json
{
  "defaultInstructions": "You are a senior software engineer. When helping with code: 1) Explain your reasoning, 2) Write clean, production-ready code, 3) Include error handling, 4) Add comments for complex logic",

  "projectInstructions": {
    "/Users/me/projects/webstore": "This is an e-commerce app using MERN stack. Always consider: 1) Payment security (PCI compliance), 2) Inventory management, 3) Performance for high traffic"
  }
}
```

---

## TRENDING AI TOOLS & FRAMEWORKS

### 🔥 LangChain & LangGraph
**What**: Framework for building LLM applications

**LangChain**: Chains, agents, memory, tools
```python
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# Simple chain
llm = ChatOpenAI(model="gpt-4")
prompt = PromptTemplate(
    input_variables=["product"],
    template="Write a tagline for {product}"
)
chain = LLMChain(llm=llm, prompt=prompt)

result = chain.run(product="AI coding assistant")
print(result)
```

**LangGraph**: Stateful multi-agent workflows
```python
from langgraph.graph import StateGraph

# Define workflow
workflow = StateGraph()
workflow.add_node("research", research_agent)
workflow.add_node("write", writer_agent)
workflow.add_node("review", reviewer_agent)

workflow.add_edge("research", "write")
workflow.add_edge("write", "review")
workflow.add_conditional_edge("review", should_revise, "write", "end")

app = workflow.compile()
result = app.invoke({"topic": "Redis caching"})
```

---

### 🚀 Vercel AI SDK
**What**: TypeScript toolkit for building AI apps

```typescript
import { openai } from '@ai-sdk/openai'
import { streamText } from 'ai'

// Streaming AI responses
const result = await streamText({
  model: openai('gpt-4'),
  prompt: 'Explain async/await in 3 sentences'
})

for await (const chunk of result.textStream) {
  process.stdout.write(chunk)
}
```

**Features**:
- ✅ Streaming responses
- ✅ Function calling
- ✅ UI components (React hooks)
- ✅ Multiple model providers (OpenAI, Anthropic, Google)

---

### 🧪 Other Trending Tools

**v0 by Vercel**
- AI UI generator (text to React components)
- Type: "Build a login form with validation"
- Generates production-ready React + Tailwind

**Bolt.new**
- AI full-stack app builder
- Generate entire apps from prompts
- Edit and deploy in browser

**Replit Agent**
- AI that builds complete apps in Replit
- Handles frontend, backend, database, deployment

**Devin AI**
- AI software engineer
- Autonomously builds features, fixes bugs
- Plans, codes, tests, commits

**Sweep AI**
- GitHub bot that writes code
- Comment on issue: "@sweep implement login feature"
- Creates PR with implementation

---

## TIPS, TRICKS & BEST PRACTICES

### 💡 Prompt Engineering Tips

**1. Be specific**
```
❌ "Fix this code"
✅ "This function throws a TypeError when userId is null. Add input validation and return a default user object if userId is missing."
```

**2. Provide context**
```
❌ "Write a function"
✅ "Write an Express middleware function that checks if user is authenticated by verifying JWT token in Authorization header. If invalid, return 401. If valid, attach decoded user to req.user."
```

**3. Specify format**
```
✅ "Explain in 3 bullet points"
✅ "Give me code only, no explanations"
✅ "Provide step-by-step solution"
```

**4. Use examples (few-shot)**
```
"Convert these snake_case variables to camelCase:

Example:
Input: user_name
Output: userName

Input: is_admin
Output: isAdmin

Now convert: created_at_timestamp"
```

**5. Break down complex tasks**
```
❌ "Build a full authentication system"
✅
Step 1: "Create a User model with email and password"
Step 2: "Write a register endpoint with password hashing"
Step 3: "Write a login endpoint that returns JWT"
Step 4: "Create auth middleware to verify JWT"
```

---

### ⚡ Productivity Tips

**1. Keyboard shortcuts**
- Cmd+K / Ctrl+K: Quick actions (Cursor, VS Code)
- Cmd+P / Ctrl+P: File search
- Cmd+Shift+F / Ctrl+Shift+F: Global search
- F2: Rename symbol across all files

**2. Use AI for boilerplate**
```
"Generate a REST API with Express for a Todo model with CRUD operations, input validation, and error handling"

// AI generates hundreds of lines in seconds
```

**3. Let AI write tests**
```
"Write unit tests for this function using Jest. Test: 1) Success case, 2) Null input, 3) Invalid format, 4) Network error"
```

**4. AI for documentation**
```
"Add JSDoc comments to all functions in this file"

"Generate a README for this project"

"Create API documentation in Markdown format"
```

**5. Refactoring**
```
"Refactor this code to: 1) Extract repeated logic into helper functions, 2) Improve variable names, 3) Add error handling"
```

---

### 🎯 Best Practices

**1. Always review AI code**
- AI can make mistakes
- Check for security issues
- Verify logic correctness

**2. Don't blindly copy-paste**
- Understand what the code does
- Adapt to your codebase style
- Check for edge cases

**3. Use AI as assistant, not replacement**
- You're still the architect
- AI is a tool, not a crutch
- Learn from AI suggestions

**4. Keep context small**
- Don't dump entire files
- Select relevant code sections
- Clear, focused questions

**5. Iterate**
- First draft might not be perfect
- Ask for improvements
- Refine through conversation

---

## INTERVIEW QUESTIONS

**Q: What is MCP?**
A: Model Context Protocol. Standard way to connect AI assistants with external data sources and tools. Like USB for AI.

**Q: Difference between GitHub Copilot and Cursor?**
A: Copilot is inline autocomplete (faster). Cursor is chat interface with codebase understanding (better for complex tasks).

**Q: How to improve AI code suggestions?**
A: 1) Write clear comments, 2) Use descriptive names, 3) Maintain consistent style, 4) Provide context in prompts.

**Q: Security concerns with AI assistants?**
A: - Don't share secrets/API keys
   - Review AI code for vulnerabilities
   - Be careful with proprietary code
   - Use enterprise versions for sensitive work

**Q: Can AI replace developers?**
A: No. AI is a tool that makes developers more productive. Still need human judgment, architecture decisions, business logic.

**Q: Best use cases for AI coding assistants?**
A: - Boilerplate code
   - Unit tests
   - Documentation
   - Refactoring
   - Learning new languages/frameworks

**Q: What's the future of AI in development?**
A: - More autonomous agents (like Devin)
   - Better codebase understanding
   - Multi-agent collaboration
   - AI-powered debugging and testing
   - But humans still crucial for architecture and product decisions

---

## RESOURCES

**Learning**:
- [MCP Documentation](https://modelcontextprotocol.io)
- [LangChain Docs](https://python.langchain.com)
- [Cursor Docs](https://cursor.sh/docs)
- [Vercel AI SDK](https://sdk.vercel.ai)

**Community**:
- r/coding with AI
- Discord: LangChain, AI Engineering
- Twitter: Follow @AnthropicAI, @OpenAI, @LangChainAI

**Newsletters**:
- TLDR AI
- The Batch (DeepLearning.AI)
- Import AI

---

**Remember: AI tools are evolving FAST. Stay curious, experiment, and keep learning!** 🚀
