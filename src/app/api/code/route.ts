import { NextRequest, NextResponse } from 'next/server';
import { ConvexHttpClient } from 'convex/browser';
import { api } from '../../../../convex/_generated/api';

// Create Convex client using environment variable
const convex = new ConvexHttpClient(process.env.NEXT_PUBLIC_CONVEX_URL!);

// Handle POST requests to /api/code
export async function POST(req: NextRequest) {
  try {
    // Parse the request body to get repo URL and prompt
    const { repoUrl, prompt } = await req.json();
    
    const sessionId = `session_${Date.now()}_${Math.random().toString(36).substring(7)}`;
    
    // Log that we're starting a new coding session
    await convex.mutation(api.logs.add, {
      type: "api_start",
      message: `Starting Claude Code session for ${repoUrl}`,
      sessionId: sessionId
    });
    
    // FULL INTEGRATION: Automatically trigger Modal agent
    const { spawn } = require('child_process');
    
    try {
      const modalProcess = spawn('modal', [
        'run', 
        'modal/agent.py::run_coding_agent',
        '--repo-url', repoUrl,
        '--prompt', prompt,
        '--session-id', sessionId
      ], {
        detached: true,    
        stdio: 'ignore'   
      });
      
      // Don't wait for Modal to complete, just trigger it
      modalProcess.unref();
      
      await convex.mutation(api.logs.add, {
        type: "modal_triggered",
        message: "Modal Claude Code agent triggered automatically",
        sessionId: sessionId
      });
      
      // Return immediately while Modal works in background
      return NextResponse.json({
        success: true,
        sessionId: sessionId,
        message: "Claude Code agent started! Check Convex dashboard for real-time progress. A GitHub PR will be created automatically.",
        dashboardUrl: `${process.env.NEXT_PUBLIC_CONVEX_URL}/dashboard`,
        status: "processing"
      });
      
    } catch (modalError: any) {
      await convex.mutation(api.logs.add, {
        type: "modal_error",
        message: `Failed to start Modal agent: ${modalError?.message || 'Unknown error'}`,
        sessionId: sessionId
      });
      
      return NextResponse.json({
        success: false,
        sessionId: sessionId,
        error: "Failed to start Claude Code agent",
        message: "Please check that Modal is installed and configured"
      }, { status: 500 });
    }
    
  } catch (error: unknown) {
    console.error('API Error:', error);
    
    // Safely extract error message
    const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
    
    return NextResponse.json(
      { 
        success: false,
        error: 'Failed to start Claude Code session',
        message: errorMessage 
      },
      { status: 500 }
    );
  }
}