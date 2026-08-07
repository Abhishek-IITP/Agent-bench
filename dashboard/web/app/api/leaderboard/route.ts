import { NextResponse } from "next/server";
import { sql } from "@/lib/db";

export async function GET() {
  try {
    const leaderboard = await sql`
      SELECT a.id, a.name, a.type, a.model,
             count(r.id) as total_runs,
             count(r.id) FILTER (WHERE r.success = true) as successful_runs,
             round(CAST(count(r.id) FILTER (WHERE r.success = true) AS NUMERIC) / NULLIF(count(r.id), 0), 4) as success_rate,
             avg(r.duration) as avg_duration,
             avg(em.tokens_used) as avg_tokens,
             sum(em.cost) as total_cost
      FROM agents a
      LEFT JOIN runs r ON r.agent_id = a.id
      LEFT JOIN execution_metrics em ON em.run_id = r.id
      GROUP BY a.id, a.name, a.type, a.model
      ORDER BY success_rate DESC NULLS LAST, total_runs DESC
    `;

    return NextResponse.json({ agents: leaderboard });
  } catch (error) {
    console.error("Error fetching leaderboard:", error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Failed to fetch leaderboard" },
      { status: 500 }
    );
  }
}
