import { NextResponse } from "next/server"

// Server-side proxy to the Python FastAPI backend. Keeps the backend URL on the
// server and avoids browser CORS. Override with BACKEND_URL in the environment.
const BACKEND_URL = process.env.BACKEND_URL ?? "http://127.0.0.1:8000"

export async function POST(request: Request) {
  let body: { query?: string; user_id?: string; top_k?: number }
  try {
    body = await request.json()
  } catch {
    return NextResponse.json({ error: "Invalid JSON body" }, { status: 400 })
  }

  if (!body.query || !body.query.trim()) {
    return NextResponse.json({ error: "Query is required" }, { status: 400 })
  }

  try {
    const res = await fetch(`${BACKEND_URL}/api/search`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        query: body.query,
        user_id: body.user_id ?? null,
        top_k: body.top_k ?? 6,
      }),
      // The engine can take a couple of seconds (zero-shot classification on CPU).
      cache: "no-store",
    })

    if (!res.ok) {
      const text = await res.text()
      return NextResponse.json(
        { error: `Backend error (${res.status}): ${text.slice(0, 300)}` },
        { status: 502 },
      )
    }

    const data = await res.json()
    return NextResponse.json(data)
  } catch (err) {
    return NextResponse.json(
      {
        error:
          "Could not reach the NLP backend. Start it with `python api_server.py` (or `uvicorn api_server:app --port 8000`).",
        detail: err instanceof Error ? err.message : String(err),
      },
      { status: 503 },
    )
  }
}
