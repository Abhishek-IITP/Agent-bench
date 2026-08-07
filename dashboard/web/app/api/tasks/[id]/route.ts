import { NextResponse } from "next/server";
import { sql } from "@/lib/db";

export async function GET(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const tasks = await sql`
      SELECT id, name, category, difficulty, version, timeout, docker_image, description, created_at
      FROM tasks
      WHERE id = ${id}
      LIMIT 1
    `;

    if (tasks.length === 0) {
      return NextResponse.json({ error: `Task not found: ${id}` }, { status: 404 });
    }

    const runs = await sql`
      SELECT count(*) as total_runs,
             count(*) FILTER (WHERE success = true) as successful_runs,
             avg(duration) as avg_duration
      FROM runs
      WHERE task_id = ${id}
    `;

    return NextResponse.json({
      task: tasks[0],
      stats: runs[0] || { total_runs: 0, successful_runs: 0, avg_duration: 0 },
    });
  } catch (error) {
    console.error("Error fetching task by ID:", error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Failed to fetch task" },
      { status: 500 }
    );
  }
}
