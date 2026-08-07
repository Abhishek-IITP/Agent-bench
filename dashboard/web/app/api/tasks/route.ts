import { NextResponse } from "next/server";
import { sql } from "@/lib/db";

export async function GET() {
  try {
    const tasks = await sql`
      SELECT id, name, category, difficulty, version, timeout, docker_image, description, created_at
      FROM tasks
      ORDER BY created_at DESC
    `;
    return NextResponse.json({ tasks });
  } catch (error) {
    console.error("Error fetching tasks:", error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Failed to fetch tasks" },
      { status: 500 }
    );
  }
}
