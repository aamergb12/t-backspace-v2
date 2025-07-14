# t-backspace-v2
Tiny Backspace - Deep Implementation Guide
Architecture Overview
This implementation uses their preferred stack:

TypeScript with Next.js API routes
Modal for secure sandboxing
Claude SDK as the coding agent
Convex for real-time logging/telemetry
GitHub CLI for PR creation

How It Works - Deep Dive
1. File Reading Mechanism
Question: "How does your code read files?"
Your code reads files in two layers:

In the Modal sandbox (coding_agent.py):

pythondef read_file(filepath):
    """This is the actual file reading mechanism"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        return f"Error reading file: {str(e)}"

Through Claude's tool system:

Claude calls the read_file tool
The tool executes in the Modal sandbox
Returns file contents to Claude for analysis
Claude then decides what to do with the content



Key Points:

Files are read inside the Modal sandbox (isolated environment)
Uses standard Python file I/O with UTF-8 encoding
Error handling for missing files or encoding issues
Contents are passed back to Claude for processing

2. GitHub PR Creation Process
Question: "How does your code make a GitHub PR?"
The PR creation happens through multiple steps:

Authentication Setup:

pythongithub_token = os.environ["GITHUB_TOKEN"]
subprocess.run(["gh", "auth", "login", "--with-token"], 
               input=github_token, text=True)

Branch Creation:

python# Claude calls run_command tool with:
run_command("git checkout -b feature/my-new-feature")

Commit Changes:

pythonrun_command("git add .")
run_command("git commit -m 'Implement requested changes'")

Push and Create PR:

pythonrun_command("git push origin feature/my-new-feature")
run_command("gh pr create --title 'Feature Title' --body 'Description'")
Key Points:

Uses GitHub CLI (gh) tool, not GitHub API directly
Authentication via PAT (Personal Access Token)
All git operations happen in the Modal sandbox
Claude orchestrates the entire workflow through tool calls

3. Sandboxing with Modal
How Modal Provides Security:

Isolated Execution Environment:

python@app.function(
    image=image,
    secrets=[modal.Secret.from_name("github-token")],
    timeout=1800
)

Temporary File System:

pythonwith tempfile.TemporaryDirectory() as tmp_dir:
    repo_path = Path(tmp_dir) / "repo"
    # All file operations happen here
    # Directory is automatically cleaned up

No Host System Access:

Code runs in containerized environment
No access to your local machine
Network access is controlled
Process dies after timeout



4. Real-time Streaming
How the streaming works:

Server-Sent Events (SSE):

typescriptconst stream = new ReadableStream({
  start(controller) {
    const encoder = new TextEncoder();
    
    const sendEvent = (data: any) => {
      const formatted = `data: ${JSON.stringify(data)}\n\n`;
      controller.enqueue(encoder.encode(formatted));
    };

Modal Output Parsing:

pythondef emit_event(data):
    print(json.dumps(data))  # Stdout goes to Node.js process
    sys.stdout.flush()

Event Flow:

Modal prints JSON to stdout
Node.js process captures stdout
Parses JSON and sends via SSE
Frontend receives real-time updates



5. Telemetry with Convex
How logging works:

Event Capture:

typescript// Log to Convex
convex.mutation('logs:create', {
  type: 'agent_output',
  data: parsed,
  timestamp: Date.now()
});

Storage Schema:

typescriptlogs: defineTable({
  type: v.string(),
  data: v.optional(v.any()),
  repoUrl: v.optional(v.string()),
  prompt: v.optional(v.string()),
  timestamp: v.number(),
})

Real-time Queries:

typescriptexport const getAll = query({
  handler: async (ctx) => {
    return await ctx.db.query("logs").order("desc").take(100);
  },
});
Setup Instructions
1. Environment Setup
bash# Install dependencies
npm install

# Install Modal CLI
pip install modal

# Install Convex CLI
npm install -g convex
2. Secrets Configuration
Modal Secrets:
bashmodal secret create anthropic-api-key
modal secret create github-token
Environment Variables:
bash# .env.local
ANTHROPIC_API_KEY=your_key_here
GITHUB_TOKEN=your_github_pat
CONVEX_URL=your_convex_url
3. Deploy Modal Function
bashmodal deploy modal/coding_agent.py
4. Setup Convex
bashnpx convex dev
5. Run Development Server
bashnpm run dev
API Usage
Endpoint: POST /api/code
Request:
json{
  "repoUrl": "https://github.com/username/repo",
  "prompt": "Add input validation to all POST endpoints"
}
Response (SSE Stream):
data: {"type": "status", "message": "Cloning repository..."}
data: {"type": "tool_call", "tool": "read_file", "input": {"filepath": "app.py"}}
data: {"type": "tool_result", "tool": "read_file", "result": "file contents..."}
Key Technical Interview Points
Security Considerations

Sandboxing: Code runs in isolated Modal containers
Temporary Storage: Files are automatically cleaned up
Secret Management: API keys stored securely in Modal
Network Isolation: Limited external access

Error Handling

File Operations: Graceful handling of missing files
Git Operations: Proper error reporting for git failures
Tool Timeouts: Commands timeout after 30 seconds
Process Management: Modal functions have 30-minute timeout

Performance Optimizations

Streaming: Real-time updates prevent blocking
Concurrent Operations: Multiple tool calls can happen in sequence
Resource Limits: Modal provides CPU/memory constraints
Cleanup: Automatic resource cleanup after completion

Observability

Real-time Telemetry: Every action logged to Convex
Tool Tracing: Each tool call and result is tracked
Error Reporting: Detailed error messages streamed back
Performance Metrics: Timestamps for all operations

Testing the Implementation
Local Testing
bashcurl -X POST http://localhost:3000/api/code \
  -H "Content-Type: application/json" \
  -d '{"repoUrl": "https://github.com/username/test-repo", "prompt": "Add a hello world endpoint"}'
Expected Output Flow

Repository cloning
Structure analysis
File reading operations
Code modifications
Git branch creation
Commit and push
PR creation
Final result with PR URL

This implementation gives you deep understanding of:

How files are read in the sandbox
How GitHub PRs are created via CLI
How the streaming architecture works
How telemetry is collected and stored
How the entire system scales securely
