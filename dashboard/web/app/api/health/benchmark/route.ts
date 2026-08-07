import { NextResponse } from "next/server";
import { sql } from "@/lib/db";

export async function GET() {
  try {
    const tasksCount = await sql`SELECT count(*) as count FROM tasks`;
    const runsCount = await sql`SELECT count(*) as count FROM runs`;
    const agentsCount = await sql`SELECT count(*) as count FROM agents`;
    const healthStatus = await sql`SELECT health_status, count(*) as count FROM task_health GROUP BY health_status`;

    return NextResponse.json({
      status: "healthy",
      database: "connected",
      stats: {
        tasks: parseInt(tasksCount[0]?.count || "0"),
        runs: parseInt(runsCount[0]?.count || "0"),
        agents: parseInt(agentsCount[0]?.count || "0"),
      },
      task_health_breakdown: healthStatus,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error("Error fetching benchmark health:", error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Failed to fetch benchmark health" },
      { status: 500 }
    );
  }
}
