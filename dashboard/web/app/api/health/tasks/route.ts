import { NextResponse } from "next/server";
import { sql } from "@/lib/db";

export async function GET() {
  try {
    const taskHealths = await sql`
      SELECT th.task_id, t.name as task_name, th.health_status, th.success_rate, th.variance, th.n_agents, th.n_runs_total, th.recommendations, th.analyzed_at
      FROM task_health th
      JOIN tasks t ON th.task_id = t.id
      ORDER BY th.health_status ASC
    `;

    return NextResponse.json({ task_healths: taskHealths });
  } catch (error) {
    console.error("Error fetching task health:", error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Failed to fetch task health" },
      { status: 500 }
    );
  }
}
