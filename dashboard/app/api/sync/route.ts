import { NextRequest, NextResponse } from "next/server";

// Cloudflare KV REST API configuration
// Set these in Vercel environment variables:
// - CF_ACCOUNT_ID: Your Cloudflare account ID
// - CF_KV_NAMESPACE_ID: Your KV namespace ID
// - CF_API_TOKEN: API token with KV read/write permissions

const CF_ACCOUNT_ID = process.env.CF_ACCOUNT_ID;
const CF_KV_NAMESPACE_ID = process.env.CF_KV_NAMESPACE_ID;
const CF_API_TOKEN = process.env.CF_API_TOKEN;

const KV_BASE_URL = `https://api.cloudflare.com/client/v4/accounts/${CF_ACCOUNT_ID}/storage/kv/namespaces/${CF_KV_NAMESPACE_ID}`;

// Rate limiting (simple in-memory, resets on cold start)
const rateLimitMap = new Map<string, { count: number; resetAt: number }>();
const RATE_LIMIT = 10; // requests per minute
const RATE_WINDOW = 60 * 1000; // 1 minute

function checkRateLimit(ip: string): boolean {
  const now = Date.now();
  const entry = rateLimitMap.get(ip);

  if (!entry || now > entry.resetAt) {
    rateLimitMap.set(ip, { count: 1, resetAt: now + RATE_WINDOW });
    return true;
  }

  if (entry.count >= RATE_LIMIT) {
    return false;
  }

  entry.count++;
  return true;
}

async function kvGet(key: string): Promise<any | null> {
  const response = await fetch(`${KV_BASE_URL}/values/${encodeURIComponent(key)}`, {
    headers: {
      Authorization: `Bearer ${CF_API_TOKEN}`,
    },
  });

  if (response.status === 404) {
    return null;
  }

  if (!response.ok) {
    throw new Error(`KV GET failed: ${response.status}`);
  }

  return response.json();
}

async function kvPut(key: string, value: any): Promise<void> {
  const response = await fetch(`${KV_BASE_URL}/values/${encodeURIComponent(key)}`, {
    method: "PUT",
    headers: {
      Authorization: `Bearer ${CF_API_TOKEN}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(value),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`KV PUT failed: ${response.status} - ${error}`);
  }
}

// GET /api/sync?hash=xxx - Download encrypted data
export async function GET(request: NextRequest) {
  // Check configuration
  if (!CF_ACCOUNT_ID || !CF_KV_NAMESPACE_ID || !CF_API_TOKEN) {
    return NextResponse.json(
      { error: "Server not configured for sync" },
      { status: 503 }
    );
  }

  // Rate limiting
  const ip = request.headers.get("x-forwarded-for") || "unknown";
  if (!checkRateLimit(ip)) {
    return NextResponse.json(
      { error: "Rate limit exceeded. Try again in a minute." },
      { status: 429 }
    );
  }

  // Get hash from query params
  const hash = request.nextUrl.searchParams.get("hash");
  if (!hash || hash.length !== 64) {
    return NextResponse.json(
      { error: "Invalid or missing hash parameter" },
      { status: 400 }
    );
  }

  const metadataOnly = request.nextUrl.searchParams.get("metadata_only") === "true";

  try {
    const key = `sync:${hash}`;
    const data = await kvGet(key);

    if (!data) {
      return NextResponse.json(
        { error: "No data found for this passphrase" },
        { status: 404 }
      );
    }

    if (metadataOnly) {
      return NextResponse.json({
        updated_at: data.updated_at,
        version: data.version,
      });
    }

    return NextResponse.json(data);
  } catch (error) {
    console.error("KV GET error:", error);
    return NextResponse.json(
      { error: "Failed to retrieve data" },
      { status: 500 }
    );
  }
}

// POST /api/sync - Upload encrypted data
export async function POST(request: NextRequest) {
  // Check configuration
  if (!CF_ACCOUNT_ID || !CF_KV_NAMESPACE_ID || !CF_API_TOKEN) {
    return NextResponse.json(
      { error: "Server not configured for sync" },
      { status: 503 }
    );
  }

  // Rate limiting
  const ip = request.headers.get("x-forwarded-for") || "unknown";
  if (!checkRateLimit(ip)) {
    return NextResponse.json(
      { error: "Rate limit exceeded. Try again in a minute." },
      { status: 429 }
    );
  }

  try {
    const body = await request.json();

    // Validate required fields
    const { hash, encrypted_data, salt, iv, updated_at, version } = body;

    if (!hash || hash.length !== 64) {
      return NextResponse.json(
        { error: "Invalid or missing hash" },
        { status: 400 }
      );
    }

    if (!encrypted_data || !salt || !iv) {
      return NextResponse.json(
        { error: "Missing encryption fields (encrypted_data, salt, iv)" },
        { status: 400 }
      );
    }

    // Store in KV
    const key = `sync:${hash}`;
    const value = {
      encrypted_data,
      salt,
      iv,
      updated_at: updated_at || new Date().toISOString(),
      version: version || 1,
    };

    await kvPut(key, value);

    return NextResponse.json({
      success: true,
      message: "Data synced successfully",
    });
  } catch (error) {
    console.error("KV PUT error:", error);
    return NextResponse.json(
      { error: "Failed to store data" },
      { status: 500 }
    );
  }
}
