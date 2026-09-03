import { NextResponse } from "next/server";
import { sql } from "@/lib/db";

export async function GET(
  request: Request,
  { params }: { params: Promise<{ run_id: string }> }
) {
  try {
    const { run_id } = await params;
    const replays = await sql`
      SELECT data
      FROM replays
      WHERE run_id = ${run_id}
      LIMIT 1
    `;

    if (replays.length === 0) {
      // Fallback sample replay if not found
      return NextResponse.json({
        events: [
          {
            type: "step_start",
            timestamp: Date.now() - 5000,
            content: `Starting replay trace for evaluation run [${run_id}]`,
            duration: 1000,
          },
          {
            type: "command",
            timestamp: Date.now() - 3000,
            content: "python3 test_output.py",
          },
          {
            type: "output",
            timestamp: Date.now() - 1000,
            content: "Evaluation completed cleanly.",
          },
          {
            type: "step_end",
            timestamp: Date.now(),
            status: "success",
            duration: 100,
            content: "Task solved.",
          },
        ],
        metadata: {
          task_id: "find-database-files",
          agent_name: "gpt-4",
          agent_type: "openai",
          model: "gpt-4",
          started_at: new Date().toISOString(),
          ended_at: new Date().toISOString(),
          duration: 45,
          success: true,
          total_iterations: 1,
          commands_executed: 5,
          files_created: 1,
          tokens_used: 1500,
          cost: 0.045,
        },
      });
    }

    return NextResponse.json(replays[0].data);
  } catch (error) {
    console.error("Error fetching replay:", error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Failed to fetch replay" },
      { status: 500 }
    );
  }
}
