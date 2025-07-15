// Import the mutation function - this lets us modify data in the database
import { mutation } from "./_generated/server";
// Import validation types
import { v } from "convex/values";

// Export a function called "add" that adds new log entries to our database
export const add = mutation({
  
  // Define what parameters this function accepts and their types
  args: { 
    type: v.string(),      // What kind of event: "status", "file_read", etc.
    message: v.string(),   // Human-readable description: "Cloning repository..."
    sessionId: v.string(), // Which coding session this belongs to
  },
  
  // The actual function that runs when someone calls logs.add()
  handler: async (ctx, args) => {
    
    // Insert a new row into the "logs" table
    await ctx.db.insert("logs", {
      
      // Spread all the arguments (type, message, sessionId) into the new row
      ...args,
      
      // Automatically add the current timestamp when this log entry was created
      timestamp: Date.now(),
    });
    
    // Note: We don't return anything because this is just logging
    // The function succeeds if no error is thrown
  },
});