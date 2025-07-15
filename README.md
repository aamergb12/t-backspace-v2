# 🤖 Tiny Backspace

A production-ready AI coding agent that automatically creates GitHub pull requests from natural language prompts using Claude Code SDK.

## ⚡ Quick Demo

```bash
# Start the system
npm run dev & npx convex dev

# Create a todo app automatically
curl -X POST http://localhost:3000/api/code \
  -H "Content-Type: application/json" \
  -d '{"repoUrl": "https://github.com/user/repo", "prompt": "create a todo app with validation"}'

# Watch real-time progress: https://console.convex.dev
# Result: Complete GitHub PR with working code
```

## 🏗️ Architecture

Tiny Backspace uses a modern serverless architecture with real-time observability:

```
User Request → Next.js API → Modal Sandbox → Claude Code SDK → GitHub PR
                    ↓               ↓                ↓
               Immediate Response   Real-time Logs   Working Code
                    ↓               ↓
               Great UX        Convex Database → Live Dashboard
```

## 🚀 Features

- **One API Call**: Complete automation from prompt to PR
- **Real-time Monitoring**: Watch Claude Code work through Convex dashboard  
- **Production Ready**: Secure sandboxing, error handling, cost tracking
- **Non-blocking**: Immediate API responses, work continues in background
- **Full Observability**: Every step logged with timestamps and metadata

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **API Layer** | Next.js 13 (App Router) | HTTP handling, process spawning |
| **Compute Layer** | Modal Functions | Secure sandboxed AI execution |
| **AI Layer** | Claude Code SDK | Official Anthropic coding agent |
| **Database** | Convex | Real-time logging and observability |
| **Version Control** | GitHub CLI | Automated PR creation |

## 📁 Project Structure

```
tiny-backspace/
├── src/app/api/code/
│   └── route.ts              # API endpoint (triggers Modal)
├── convex/
│   ├── schema.ts             # Database schema definition
│   └── logs.ts               # Logging mutations
├── modal/
│   └── agent.py              # Claude Code SDK agent
└── package.json
```

## 🔧 Setup Instructions

### Prerequisites

- **Node.js 18+**
- **Python 3.9+** 
- **GitHub Personal Access Token**
- **Anthropic API Key**
- **Modal Account**
- **Convex Account**

### 1. Clone and Install

```bash
git clone https://github.com/yourusername/tiny-backspace
cd tiny-backspace
npm install
```

### 2. Environment Variables

Create `.env.local`:

```bash
NEXT_PUBLIC_CONVEX_URL=https://your-convex-url.convex.cloud
ANTHROPIC_API_KEY=sk-ant-api03-...
GITHUB_TOKEN=ghp_...
```

### 3. Set up Convex

```bash
npx convex dev
# Follow prompts to create project and deploy schema
```

### 4. Set up Modal

```bash
pip install modal
modal setup

# Create Modal secrets
modal secret create anthropic-api-key ANTHROPIC_API_KEY=sk-ant-api03-...
modal secret create github-token GITHUB_TOKEN=ghp_...
modal secret create convex-url CONVEX_URL=https://your-convex-url.convex.cloud

# Deploy the agent
modal deploy modal/agent.py
```

### 5. Start the System

```bash
# Terminal 1: Start Next.js and Convex
npm run dev & npx convex dev

# Terminal 2: Test the system
curl -X POST http://localhost:3000/api/code \
  -H "Content-Type: application/json" \
  -d '{
    "repoUrl": "https://github.com/yourusername/test-repo",
    "prompt": "create a simple contact form with validation"
  }'
```

## 🎯 How It Works

### 1. API Request
```typescript
POST /api/code
{
  "repoUrl": "https://github.com/user/repo",
  "prompt": "create a todo app"
}
```

### 2. System Flow

1. **Next.js API** receives request and generates unique session ID
2. **API logs** start event to Convex database  
3. **API spawns** Modal process in background
4. **API returns** immediately with session ID
5. **Modal agent** clones repository in secure sandbox
6. **Claude Code SDK** analyzes repo and implements feature
7. **Agent logs** every step to Convex in real-time
8. **Git operations** commit changes and push new branch
9. **GitHub CLI** creates pull request automatically
10. **Final logs** include PR URL and execution statistics

### 3. Real-time Monitoring

Watch progress at `https://console.convex.dev`:

```
[api_start] Starting Claude Code session for https://github.com/...
[setup] Setting up Claude Code SDK environment...
[git_clone] Cloning repository: https://github.com/...
[claude_init] Claude Code initialized with 15 tools
[claude_response] Claude: I'll create a todo application...
[claude_tool_write] Writing file: todo.html
[claude_tool_write] Writing file: todo.js
[success] Successfully created PR: https://github.com/.../pull/42
```

## 🏛️ Architecture Decisions

### Why Modal Functions vs Sandboxes?
- **Production-ready**: Optimized for repeated execution
- **Better logging**: Structured observability with timestamps
- **Scalability**: Concurrent execution with resource optimization
- **Security**: Proper secret injection and isolation

### Why Python Claude Code SDK vs CLI?
- **Granular control**: See every step of Claude's decision-making
- **Real-time observability**: Stream messages as they happen
- **Error handling**: Sophisticated exception management
- **Integration**: Perfect integration with logging and monitoring

### Why Convex vs Traditional Database?
- **Real-time updates**: No polling, instant dashboard updates
- **Serverless**: No database management overhead
- **Type safety**: End-to-end TypeScript integration
- **Developer experience**: Built-in dashboard and queries

### Why Write-only Logging Pattern?
- **Fast APIs**: Non-blocking responses, no query overhead
- **Separation of concerns**: Monitoring separate from application logic
- **Leverage existing tools**: Convex dashboard vs custom UI
- **Scalability**: Simple, efficient, easy to maintain

## 🔍 API Reference

### POST /api/code

Create a new coding session.

**Request:**
```json
{
  "repoUrl": "https://github.com/username/repository",
  "prompt": "Natural language description of what to implement"
}
```

**Response:**
```json
{
  "success": true,
  "sessionId": "session_1735689234567_abc123",
  "message": "Claude Code agent started! Check Convex dashboard for real-time progress.",
  "dashboardUrl": "https://your-project.convex.cloud/dashboard",
  "status": "processing"
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Failed to start Claude Code agent",
  "message": "Please check that Modal is installed and configured"
}
```

## 📊 Monitoring and Observability

### Convex Dashboard
- **Real-time logs**: See every step as it happens
- **Session grouping**: Track individual coding sessions
- **Performance metrics**: Execution time, API costs
- **Error tracking**: Full error context and stack traces

### Modal Dashboard  
- **Function executions**: Container performance and logs
- **Resource usage**: CPU, memory, duration tracking
- **Cost analysis**: Detailed billing per execution
- **Error diagnostics**: Container-level debugging

### GitHub Integration
- **Automatic PRs**: Complete with detailed descriptions
- **Branch management**: Clean, descriptive branch names
- **Commit messages**: Full context and session tracking

## 🚨 Error Handling

The system includes comprehensive error handling:

- **API level**: Invalid requests, missing parameters
- **Modal level**: Container failures, timeout handling  
- **Claude Code level**: API rate limits, permission errors
- **Git level**: Repository access, push failures
- **GitHub level**: PR creation errors, authentication issues

All errors are logged to Convex with full context for debugging.

## 💰 Cost Estimation

Typical costs per coding session:

- **Claude API**: $0.01 - $0.10 (depends on complexity)
- **Modal compute**: $0.001 - $0.005 (few minutes execution)
- **Convex operations**: <$0.001 (minimal database operations)

**Total per session**: ~$0.01 - $0.11

## 🔐 Security

- **Sandboxed execution**: Modal containers isolate all code execution
- **Secret management**: Secure credential injection via Modal secrets
- **GitHub permissions**: Tokens with minimal required scope
- **No persistent storage**: Containers are ephemeral and isolated

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes  
4. Test with a simple prompt
5. Submit a pull request

## 📜 License

MIT License - see LICENSE file for details.

## 🙋 Support

- **Issues**: GitHub Issues for bug reports
- **Documentation**: This README and inline code comments
- **Examples**: Check the repository for example prompts and use cases

---

**Built with ❤️ using Claude Code SDK, Modal, Convex, and Next.js**