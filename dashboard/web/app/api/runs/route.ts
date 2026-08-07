import { NextResponse } from "next/server";
import { sql } from "@/lib/db";

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const taskId = searchParams.get("task_id");
    const limit = Math.min(100, parseInt(searchParams.get("limit") || "50"));
    const page = Math.max(1, parseInt(searchParams.get("page") || "1"));
    const offset = (page - 1) * limit;

    let runs;
    if (taskId) {
      runs = await sql`
        SELECT r.id, r.task_id, r.agent_id, a.name as agent_name, a.model, r.started_at, r.ended_at, r.duration, r.success,
               res.score, res.test_output, em.tokens_used, em.cost
        FROM runs r
        JOIN agents a ON r.agent_id = a.id
        LEFT JOIN results res ON res.run_id = r.id
        LEFT JOIN execution_metrics em ON em.run_id = r.id
        WHERE r.task_id = ${taskId}
        ORDER BY r.created_at DESC
        LIMIT ${limit} OFFSET ${offset}
      `;
    } else {
      runs = await sql`
        SELECT r.id, r.task_id, r.agent_id, a.name as agent_name, a.model, r.started_at, r.ended_at, r.duration, r.success,
               res.score, res.test_output, em.tokens_used, em.cost
        FROM runs r
        JOIN agents a ON r.agent_id = a.id
        LEFT JOIN results res ON res.run_id = r.id
        LEFT JOIN execution_metrics em ON em.run_id = r.id
        ORDER BY r.created_at DESC
        LIMIT ${limit} OFFSET ${offset}
      `;
    }

    const countRes = await sql`SELECT count(*) as total FROM runs`;
    const total = parseInt(countRes[0]?.total || "0");

    return NextResponse.json({
      runs,
      pagination: {
        total,
        page,
        limit,
        pages: Math.ceil(total / limit),
      },
    });
  } catch (error) {
    console.error("Error fetching runs:", error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Failed to fetch runs" },
      { status: 500 }
    );
  }
}
