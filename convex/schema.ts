
import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values"; 

// Export the database schema -table structure
export default defineSchema({
  

  logs: defineTable({
    
    // Examples: "status", "file_read", "git_command", "pr_created", "error"
    type: v.string(),
    
    // Examples: "Cloning repository...", "Successfully read app.py", "Created PR #123"
    message: v.string(), 
    
    // Example: "session_abc123" - all events from one API call share this ID
    sessionId: v.string(),
    
    timestamp: v.number(),
    
  })
  .index("by_session", ["sessionId"]),
});