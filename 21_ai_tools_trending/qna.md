# AI TOOLS & TRENDING TECH Q&A

## AI CODE ASSISTANTS

**Q: What is GitHub Copilot?**
A: AI pair programmer by GitHub (powered by OpenAI). Suggests code as you type based on context and comments.

**Q: How does Copilot work?**
A: Trained on billions of lines of public code. Uses surrounding code and comments to predict what you want to write next.

**Q: Copilot vs Cursor?**
A: Copilot: Inline suggestions (fast, autocomplete-style).
   Cursor: Chat interface + codebase understanding (better for complex tasks, explanations).
   Best: Use both!

**Q: What is Claude Code?**
A: Anthropic's agentic CLI coding assistant. Runs in terminal, reads entire codebase, plans and executes multi-step tasks autonomously. Can write code, run tests, fix failures, and commit. Supports CLAUDE.md project instructions.

**Q: Claude Code vs Cursor?**
A: Claude Code: Terminal-based, agentic (autonomous multi-step tasks), no IDE needed, excellent for complex features end-to-end.
   Cursor: IDE (VS Code fork), better for interactive exploration and explanation, real-time chat.

**Q: What is Windsurf?**
A: AI-first IDE by Codeium. Has "Cascade" — an AI agent that plans and executes multi-file changes autonomously. Stronger context retention than Cursor for large codebases.

**Q: What is Lovable.dev?**
A: Full-stack app builder. Describe your app in natural language → get working React + Supabase app with auth and deployment. Perfect for MVPs. Formerly GPT Engineer.

**Q: What is Bolt.new?**
A: In-browser AI app builder (StackBlitz). No setup required — describe app, get running code in browser, export to GitHub.

**Q: Lovable.dev vs Bolt.new?**
A: Lovable: Better Supabase/backend integration, GitHub sync. Bolt: Instant browser environment, no login needed, more frameworks.

**Q: What is v0 by Vercel?**
A: AI UI generator. Prompt → React + Tailwind component. Not full apps — specialized for UI components. Uses shadcn/ui.

**Q: What is Devin AI?**
A: First "AI software engineer" by Cognition Labs. Autonomous agent that plans, codes, tests, debugs, deploys. High cost (~$500/month), meant for enterprise teams.

**Q: What is Amazon Q Developer?**
A: Amazon's AI coding assistant (formerly CodeWhisperer). Deep AWS integration, security vulnerability scanning, free for individuals, agent mode for multi-file changes.

**Q: What is Zed Editor?**
A: Native Rust editor (not Electron-based). Super fast, built-in real-time collaboration, integrated Claude/Copilot AI. Alternative to VS Code for performance-focused devs.

**Q: What is Replit Agent?**
A: AI that builds complete apps autonomously inside Replit. Handles frontend, backend, database, and deployment. Great for students and prototypes.

**Q: What is aider?**
A: Open-source AI coding assistant for terminal. Edit files with natural language commands, auto-commits changes. Works with OpenAI, Anthropic, and local models. Underrated and powerful.

**Q: Is AI-generated code secure?**
A: Not always! AI can suggest vulnerable code (SQL injection, XSS). Always review and test AI suggestions.

**Q: Can AI steal my code?**
A: Enterprise versions (Copilot Business, Cursor Pro) don't use your code for training. Free versions might. Check privacy policy.

**Q: Does Copilot make you a worse programmer?**
A: Not if used right! Like calculator vs mental math. Use AI to be productive, but still understand the code.

**Q: Best practices for AI assistants?**
A: 1) Always review code
   2) Understand what it does
   3) Test thoroughly
   4) Use for boilerplate, not learning shortcuts
   5) Keep security in mind

---

## MODEL CONTEXT PROTOCOL (MCP)

**Q: What is MCP?**
A: Model Context Protocol. Standard for connecting AI assistants with external tools and data sources.

**Q: Who created MCP?**
A: Anthropic (makers of Claude).

**Q: Why is MCP important?**
A: Before: Each AI had custom integrations (messy).
   After: One standard protocol for all (clean, reusable).
   Like USB for AI!

**Q: MCP components?**
A: 1) **Client**: AI assistant (Claude, GPT)
   2) **Server**: Your tool/integration
   3) **Protocol**: JSON-RPC (over stdio or HTTP)

**Q: What can MCP servers do?**
A: - Query databases
   - Call APIs
   - Read/write files
   - Send emails/notifications
   - Run custom business logic

**Q: Tools vs Resources in MCP?**
A: Tools: Functions AI can call (actions).
   Resources: Data AI can read (files, databases).

**Q: How to build an MCP server?**
A: 1) Define tools with descriptions
   2) Implement tool functions
   3) Handle requests via MCP protocol
   4) Configure client to use your server

**Q: Example MCP use case?**
A: Database query tool: Let Claude run SELECT queries on your PostgreSQL database and answer questions about your data.

**Q: MCP vs REST API?**
A: MCP is standardized for AI interactions (input schemas, descriptions).
   REST API is general-purpose HTTP interface.

---

## CLI TOOLS

**Q: Why use CLI over GUI?**
A: - Faster (keyboard > mouse)
   - Automatable (scripts)
   - More powerful (pipe commands)
   - Lightweight (no GUI overhead)

**Q: Essential CLI tools for developers?**
A: - `gh`: GitHub CLI
   - `jq`: JSON processor
   - `fzf`: Fuzzy finder
   - `httpie`: User-friendly HTTP client
   - `ripgrep (rg)`: Fast search
   - `bat`: Better cat (syntax highlighting)

**Q: What is `jq`?**
A: Command-line JSON processor. Filter, transform, extract data from JSON.
   ```bash
   curl api.com/users | jq '.[] | select(.age > 18) | .name'
   ```

**Q: What is `fzf`?**
A: Fuzzy finder. Quickly search and select from lists (files, command history, processes).

**Q: AI-powered CLI tools?**
A: - `aider`: AI coding assistant in terminal
   - `warp`: AI terminal with natural language commands
   - `GitHub Copilot CLI`: AI command suggestions

**Q: What is `aider`?**
A: AI coding assistant for terminal. Edit files with natural language, auto-commits changes.

---

## HOOKS, SKILLS & INSTRUCTIONS

**Q: What are Git hooks?**
A: Scripts that run automatically on Git events (pre-commit, pre-push, etc.).

**Q: Common Git hooks?**
A: - `pre-commit`: Run tests/linter before commit
   - `pre-push`: Run tests before push
   - `commit-msg`: Validate commit message format
   - `post-merge`: Run npm install after pull

**Q: What is `husky`?**
A: NPM package for easy Git hook management. Simplifies setting up hooks in projects.

**Q: What is `lint-staged`?**
A: Run linters only on staged files (fast!). Used with husky for pre-commit.

**Q: AI Skills/Instructions?**
A: Configuration files that tell AI how to behave for your project.

**Q: Examples of AI instructions?**
A: `.cursorrules`: Cursor IDE project-specific instructions
   `.github/copilot-instructions.md`: GitHub Copilot guidelines
   Claude Desktop instructions: Global AI behavior

**Q: What goes in AI instructions?**
A: - Tech stack
   - Coding standards
   - File structure
   - Security requirements
   - Common patterns
   - Things to avoid

---

## TRENDING AI FRAMEWORKS

**Q: What is LangChain?**
A: Framework for building LLM applications. Provides chains, agents, memory, tools for complex AI workflows.

**Q: LangChain use cases?**
A: - Chatbots with memory
   - Document Q&A (RAG)
   - Autonomous agents
   - Multi-step reasoning
   - Tool-using AI

**Q: What is LangGraph?**
A: Extension of LangChain for stateful multi-agent workflows. Build complex AI systems with multiple agents collaborating.

**Q: What is Vercel AI SDK?**
A: TypeScript toolkit for building AI apps. Streaming responses, function calling, UI components (React hooks).

**Q: What is RAG?**
A: Retrieval-Augmented Generation. Fetch relevant documents, feed to LLM with user question.
   Prevents hallucination, uses your data!

**Q: What is function calling?**
A: LLM decides which function to call based on user request, provides arguments. Enables AI to use tools.

**Q: What is prompt engineering?**
A: Crafting effective prompts to get best AI responses. Clear instructions, examples, context.

---

## NEW AI TOOLS

**Q: What is v0 by Vercel?**
A: AI UI generator. Describe UI in text, get React + Tailwind code. "Build a pricing table with 3 tiers"

**Q: What is Bolt.new?**
A: AI full-stack app builder. Generate entire apps from prompts, edit and deploy in browser.

**Q: What is Replit Agent?**
A: AI that builds complete apps in Replit. Handles frontend, backend, database, deployment autonomously.

**Q: What is Devin AI?**
A: AI software engineer. Plans, codes, tests, commits. Autonomously implements features and fixes bugs.

**Q: What is Sweep AI?**
A: GitHub bot that writes code. Comment "@sweep implement auth system", it creates PR with implementation.

**Q: Will AI replace developers?**
A: No! AI is a productivity tool. Humans still needed for:
   - Architecture decisions
   - Business logic
   - Product strategy
   - Code review
   - Edge cases & security

**Q: What jobs are most at risk from AI?**
A: - Junior developers doing pure coding
   - QA testers (AI can generate tests)
   - Technical writers (AI documentation)

**Q: What jobs are safest from AI?**
A: - Senior engineers (architecture, system design)
   - Product managers (user needs, strategy)
   - DevOps/SREs (production systems)
   - Security engineers (threat modeling)

---

## PRODUCTIVITY & BEST PRACTICES

**Q: Prompt engineering tips?**
A: 1) Be specific
   2) Provide context
   3) Specify format
   4) Use examples (few-shot)
   5) Break down complex tasks

**Q: How to get better AI code?**
A: - Write clear comments
   - Use descriptive variable names
   - Provide context in prompts
   - Iterate and refine
   - Specify constraints

**Q: When to use AI assistance?**
A: ✅ Boilerplate code
   ✅ Unit tests
   ✅ Documentation
   ✅ Refactoring
   ✅ Code explanations
   ✅ Learning new tech

**Q: When NOT to use AI?**
A: ❌ Critical security code
   ❌ Complex business logic (without review)
   ❌ Learning fundamentals
   ❌ Production code without testing

**Q: How to review AI code?**
A: 1) Understand what it does
   2) Check for security issues (SQL injection, XSS, etc.)
   3) Test edge cases
   4) Verify logic correctness
   5) Ensure it fits codebase style

**Q: AI coding interview tips?**
A: - Don't use AI during coding interviews (cheating!)
   - Use AI to practice (generate problems)
   - Use AI to understand solutions
   - But solve problems yourself first

---

## SECURITY & ETHICS

**Q: Privacy concerns with AI assistants?**
A: - Code sent to cloud servers
   - Potential training on your code
   - Leaking proprietary information

   Mitigation:
   - Use enterprise versions (no training)
   - Don't share secrets/API keys
   - Review privacy policies

**Q: Can AI suggest copyrighted code?**
A: Rare, but possible. Copilot trained on public GitHub code. Mostly generates original code, but can replicate if very common.

**Q: Ethical considerations?**
A: - Job displacement (junior devs)
   - Code quality (over-reliance on AI)
   - Attribution (who owns AI-generated code?)
   - Bias (AI trained on potentially biased code)

**Q: How to use AI ethically?**
A: - Review and understand AI code
   - Don't claim AI work as entirely yours
   - Consider impact on jobs/learning
   - Use responsibly (don't automate harmful things)

---

## FUTURE TRENDS

**Q: Where is AI coding headed?**
A: - More autonomous agents (less human intervention)
   - Better codebase understanding (entire projects)
   - Multi-agent collaboration (multiple AIs working together)
   - AI-powered debugging and testing
   - Voice coding (speak, AI writes code)

**Q: What to learn to stay relevant?**
A: - **System design** (AI can't replace architecture decisions)
   - **Product thinking** (understanding user needs)
   - **AI/ML fundamentals** (be AI-literate)
   - **Prompt engineering** (how to use AI effectively)
   - **Code review** (evaluating AI-generated code)

**Q: Skills that become more important?**
A: - Critical thinking
   - Problem decomposition
   - Communication
   - System design
   - Security expertise
   - Domain knowledge

**Q: Skills that become less important?**
A: - Syntax memorization
   - Boilerplate code writing
   - Basic CRUD operations
   - Simple debugging

**Q: How to future-proof your career?**
A: - Master fundamentals (algorithms, system design)
   - Learn to work WITH AI (prompt engineering)
   - Focus on architecture and product
   - Build domain expertise
   - Never stop learning

---

## RAPID FIRE

**Q: Best free AI coding assistant?**
A: Codeium (free forever) or Cursor free tier.

**Q: Best paid AI coding assistant?**
A: Cursor Pro ($20/mo) for exploration, GitHub Copilot ($10/mo) for autocomplete.

**Q: Best AI for learning?**
A: ChatGPT or Claude (explain concepts, provide examples).

**Q: Best CLI for productivity?**
A: `fzf` + `zoxide` + `bat` + `ripgrep`

**Q: Best Git hook tool?**
A: `husky` + `lint-staged`

**Q: Should I learn Vim?**
A: Optional, but huge productivity boost if you do.

**Q: Best way to learn AI tools?**
A: Just start using them! Experiment, make mistakes, iterate.

**Q: Most overhyped AI tool?**
A: (Opinion) Some "AI that codes for you" tools. Still need human oversight!

**Q: Most underrated AI tool?**
A: `aider` — AI coding in terminal. Underrated but powerful!
