# Use your original agent.py that was working last night
# This is the clean version without debug logs

import modal
import subprocess
import os
import tempfile
import json
import requests
import asyncio

# Create Modal image with REAL Claude Code SDK
image = modal.Image.debian_slim().pip_install([
    "requests",           # HTTP calls to Convex
    "claude-code-sdk",    # Official Claude Code Python SDK
    "anyio",              # Required for Claude Code SDK async operations
]).apt_install([
    "git",                # Git CLI for repository operations
    "gh",                 # GitHub CLI for PR creation
    "nodejs",             # Node.js (required by Claude Code SDK)
    "npm"                 # NPM (required by Claude Code SDK)
]).run_commands([
    # Install Claude Code CLI (required by Python SDK)
    "npm install -g @anthropic-ai/claude-code"
])

# Create Modal app
app = modal.App("tiny-backspace-v2")

@app.function(
    image=image,
    # Secrets needed for Claude Code SDK
    secrets=[
        modal.Secret.from_name("anthropic-api-key"),   # Claude API key
        modal.Secret.from_name("github-token"),        # GitHub Personal Access Token
        modal.Secret.from_name("convex-url"),          # Convex database URL
    ],
    timeout=1800  # 30 minute timeout
)
async def run_coding_agent(repo_url: str, prompt: str, session_id: str):
    """
    Run Claude Code using the OFFICIAL Claude Code Python SDK
    """
    
    def log_to_convex(log_type: str, message: str):
        """Log events back to Convex for real-time observability"""
        try:
            convex_url = os.environ["CONVEX_URL"]
            response = requests.post(f"{convex_url}/api/mutation", 
                json={
                    "path": "logs:add",
                    "args": {
                        "type": log_type,
                        "message": message,
                        "sessionId": session_id
                    }
                },
                headers={"Content-Type": "application/json"}
            )
            print(f"[{log_type}] {message} (Convex: {response.status_code})")
        except Exception as e:
            print(f"[{log_type}] {message} (Convex failed: {e})")
    
    try:
        # Import the official Claude Code SDK
        from claude_code_sdk import query, ClaudeCodeOptions
        from pathlib import Path
        
        # STEP 1: Setup environment
        log_to_convex("setup", "Setting up Claude Code SDK environment...")
        
        # Set API key for Claude Code SDK
        os.environ["ANTHROPIC_API_KEY"] = os.environ["ANTHROPIC_API_KEY"]
        
        # Setup GitHub authentication
        github_token = os.environ["GITHUB_TOKEN"]
        subprocess.run(["gh", "auth", "login", "--with-token"], 
                      input=github_token, text=True, check=False)
        
        # Configure git with proper credentials
        subprocess.run(["git", "config", "--global", "user.email", "claude-code@backspace.run"], check=False)
        subprocess.run(["git", "config", "--global", "user.name", "Claude Code SDK Agent"], check=False)
        subprocess.run(["git", "config", "--global", "credential.helper", "store"], check=False)
        
        log_to_convex("auth_complete", "Authentication setup completed")
        
        # STEP 2: Clone repository
        log_to_convex("git_clone", f"Cloning repository: {repo_url}")
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_path = f"{tmp_dir}/repo"
            
            # Clone the repository
            clone_result = subprocess.run([
                "git", "clone", repo_url, repo_path
            ], capture_output=True, text=True)
            
            if clone_result.returncode != 0:
                error_msg = f"Failed to clone repository: {clone_result.stderr}"
                log_to_convex("error", error_msg)
                return {"success": False, "error": error_msg}
            
            # Change to repository directory
            os.chdir(repo_path)
            
            # Configure git remote for token authentication
            repo_name = repo_url.split('/')[-1].replace('.git', '')
            username = repo_url.split('/')[-2]
            token_url = f"https://{github_token}@github.com/{username}/{repo_name}.git"
            subprocess.run(["git", "remote", "set-url", "origin", token_url], check=False)
            
            log_to_convex("repo_ready", "Repository cloned and configured")
            
            # STEP 3: Create branch for changes
            branch_name = f"claude-code/{prompt.lower().replace(' ', '-').replace('.', '').replace('/', '-')[:50]}"
            subprocess.run(["git", "checkout", "-b", branch_name], check=False)
            log_to_convex("branch_created", f"Created branch: {branch_name}")
            
            # STEP 4: Configure Claude Code SDK options
            log_to_convex("claude_config", "Configuring Claude Code SDK...")
            
            # Create Claude Code options with proper permissions
            options = ClaudeCodeOptions(
                max_turns=10,                           # Limit turns for safety
                cwd=Path(repo_path),                    # Set working directory to repo
                allowed_tools=["Read", "Write", "Bash"], # Enable all necessary tools
                permission_mode="acceptEdits"           # Auto-approve file edits
            )
            
            log_to_convex("claude_ready", "Claude Code SDK configured with full permissions")
            
            # STEP 5: Execute coding task using Claude Code SDK
            log_to_convex("claude_start", f"Starting Claude Code SDK: {prompt}")
            
            # Collect all messages from Claude Code
            messages = []
            total_cost = 0.0
            
            try:
                # Use the official Claude Code SDK query function
                async for message in query(
                    prompt=prompt,
                    options=options
                ):
                    messages.append(message)
                    
                    # Handle different Claude Code SDK message types
                    if hasattr(message, '__class__'):
                        class_name = message.__class__.__name__
                        
                        if class_name == "SystemMessage":
                            if hasattr(message, 'data') and message.data.get('subtype') == 'init':
                                tools = message.data.get('tools', [])
                                log_to_convex("claude_init", f"Claude Code initialized with {len(tools)} tools")
                        
                        elif class_name == "AssistantMessage":
                            if hasattr(message, 'content'):
                                for content_block in message.content:
                                    if hasattr(content_block, '__class__'):
                                        if content_block.__class__.__name__ == "TextBlock":
                                            text = getattr(content_block, 'text', '')
                                            log_to_convex("claude_response", f"Claude: {text[:100]}")
                                        
                                        elif content_block.__class__.__name__ == "ToolUseBlock":
                                            tool_name = getattr(content_block, 'name', 'unknown')
                                            log_to_convex("claude_tool", f"Tool: {tool_name}")
                        
                        elif class_name == "ResultMessage":
                            if hasattr(message, 'num_turns'):
                                log_to_convex("claude_result", f"Completed with {message.num_turns} turns")
                            if hasattr(message, 'total_cost_usd'):
                                total_cost = message.total_cost_usd
                                log_to_convex("claude_cost", f"Cost: ${total_cost:.4f}")
                
                log_to_convex("claude_success", f"Claude Code SDK completed with {len(messages)} messages")
                claude_output = "Claude Code completed successfully"
                
            except Exception as claude_error:
                log_to_convex("claude_error", f"Claude Code SDK error: {str(claude_error)}")
                claude_output = f"Error: {str(claude_error)}"
            
            # STEP 6: Check for changes and commit
            log_to_convex("git_check", "Checking for changes...")
            
            git_status = subprocess.run(["git", "status", "--porcelain"], 
                                      capture_output=True, text=True)
            
            if git_status.stdout.strip():
                log_to_convex("changes_found", f"Found changes: {len(git_status.stdout.strip().split())} files")
                
                subprocess.run(["git", "add", "-A"], check=False)
                
                commit_message = f"""Implement: {prompt}

Implemented by Claude Code SDK
Session: {session_id}
Messages: {len(messages)}
Cost: ${total_cost:.4f}

Summary: {claude_output}"""
                
                commit_result = subprocess.run([
                    "git", "commit", "-m", commit_message
                ], capture_output=True, text=True, check=False)
                
                if commit_result.returncode == 0:
                    log_to_convex("git_committed", "Successfully committed changes")
                else:
                    log_to_convex("git_commit_failed", f"Commit failed: {commit_result.stderr}")
                    
            else:
                log_to_convex("no_changes", "No changes detected from Claude Code")
                subprocess.run([
                    "git", "commit", "--allow-empty", "-m",
                    f"Claude Code SDK session: {prompt}\n\nSession: {session_id}"
                ], check=False)
            
            # STEP 7: Push and create PR
            log_to_convex("pr_start", "Creating pull request...")
            
            push_result = subprocess.run([
                "git", "push", "origin", branch_name
            ], capture_output=True, text=True, check=False)
            
            if push_result.returncode == 0:
                log_to_convex("push_success", f"Successfully pushed branch: {branch_name}")
                
                pr_title = f"Claude Code SDK: {prompt}"
                pr_body = f"""## Implementation by Claude Code SDK

**Task**: {prompt}

**Implementation Summary**:
{claude_output}

**Technical Details**:
- **Agent**: Claude Code SDK (Official Anthropic Python SDK)
- **Session ID**: {session_id}
- **Branch**: {branch_name}
- **Messages Processed**: {len(messages)}
- **Total Cost**: ${total_cost:.4f} USD

Generated automatically by Tiny Backspace coding agent.
"""
                
                pr_result = subprocess.run([
                    "gh", "pr", "create",
                    "--title", pr_title,
                    "--body", pr_body,
                    "--base", "main"
                ], capture_output=True, text=True, check=False)
                
                if pr_result.returncode == 0:
                    pr_url = pr_result.stdout.strip()
                    log_to_convex("success", f"Successfully created PR: {pr_url}")
                    
                    return {
                        "success": True,
                        "prUrl": pr_url,
                        "message": f"Claude Code SDK successfully implemented: {prompt}",
                        "branch": branch_name,
                        "summary": claude_output
                    }
                else:
                    error_msg = f"Failed to create PR: {pr_result.stderr}"
                    log_to_convex("pr_failed", error_msg)
                    return {"success": False, "error": error_msg}
            else:
                error_msg = f"Failed to push branch: {push_result.stderr}"
                log_to_convex("push_failed", error_msg)
                return {"success": False, "error": error_msg}
    
    except ImportError as import_error:
        error_msg = f"Claude Code SDK not available: {str(import_error)}"
        log_to_convex("sdk_missing", error_msg)
        return {"success": False, "error": error_msg}
    
    except Exception as e:
        error_msg = f"Claude Code SDK agent failed: {str(e)}"
        log_to_convex("fatal_error", error_msg)
        return {"success": False, "error": error_msg}

# Export for deployment
if __name__ == "__main__":
    modal.run()