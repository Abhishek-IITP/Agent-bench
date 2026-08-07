import { NextResponse } from "next/server";
import { sql } from "@/lib/db";

export async function GET(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const runs = await sql`
      SELECT r.id, r.task_id, r.agent_id, a.name as agent_name, a.model, r.started_at, r.ended_at, r.duration, r.success,
             res.score, res.test_output, res.test_details, em.commands_executed, em.files_created, em.files_modified, em.tokens_used, em.cost
      FROM runs r
      JOIN agents a ON r.agent_id = a.id
      LEFT JOIN results res ON res.run_id = r.id
      LEFT JOIN execution_metrics em ON em.run_id = r.id
      WHERE r.id = ${id}
      LIMIT 1
    `;

    if (runs.length === 0) {
      return NextResponse.json({ error: `Run not found: ${id}` }, { status: 404 });
    }

    return NextResponse.json({ run: runs[0] });
  } catch (error) {
    console.error("Error fetching run details:", error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Failed to fetch run" },
      { status: 500 }
    );
  }
}
