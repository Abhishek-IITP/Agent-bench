import { NextResponse } from "next/server";

const formspreeUrl = process.env.NEXT_PUBLIC_FORMSPREE_URL ?? "https://formspree.io/f/mnjkgpwg";

export async function POST(request: Request) {
  const body = (await request.json().catch(() => null)) as { email?: string } | null;

  if (!body?.email) {
    return NextResponse.json({ error: "Email is required." }, { status: 400 });
  }

  try {
    const response = await fetch(formspreeUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify({ email: body.email }),
    });

    if (!response.ok) {
      return NextResponse.json({ error: "Submission failed." }, { status: response.status });
    }

    return NextResponse.json({ ok: true });
  } catch {
    return NextResponse.json({ error: "Submission failed." }, { status: 500 });
  }
}