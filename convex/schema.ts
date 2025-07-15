// Import the functions we need to define our database structure
import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values"; // 'v' stands for 'validation' - defines data types

// Export the database schema - this is like creating a table structure
export default defineSchema({
  
  // Create a table called "logs" to store all our telemetry data
  logs: defineTable({
    
    // type: What kind of event this is (required string)
    // Examples: "status", "file_read", "git_command", "pr_created", "error"
    type: v.string(),
    
    // message: Human-readable description of what happened (required string)
    // Examples: "Cloning repository...", "Successfully read app.py", "Created PR #123"
    message: v.string(), 
    
    // sessionId: Unique ID that groups all events from one coding session (required string)
    // Example: "session_abc123" - all events from one API call share this ID
    sessionId: v.string(),
    
    // timestamp: When this event happened in milliseconds (required number)
    // Example: 1703123456789 - automatically set when we insert the log
    timestamp: v.number(),
    
  })
  // Create an index for fast lookups by sessionId
  // This makes queries like "show me all logs for session X" super fast
  // Without this index, database would have to scan every single row
  .index("by_session", ["sessionId"]),
});