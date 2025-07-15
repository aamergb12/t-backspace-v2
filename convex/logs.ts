// Import the mutation function - this lets us modify data in the database
import { mutation } from "./_generated/server";
import { v } from "convex/values";

// Export function "add" that adds new logs to db
export const add = mutation({
  
  args: { 
    type: v.string(),     
    message: v.string(),   
    sessionId: v.string(), 
  },
  
  // The actual function that runs when someone calls logs.add()
  handler: async (ctx, args) => {
    
    // Insert a new row into the "logs" table
    await ctx.db.insert("logs", {
      
      ...args,
      
      timestamp: Date.now(),
    });
    
  },
});