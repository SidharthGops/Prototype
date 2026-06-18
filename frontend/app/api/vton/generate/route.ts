import { NextResponse } from "next/server";

const BACKEND_BASE_URL =
  process.env.VTON_BACKEND_URL ?? "http://127.0.0.1:8000";
const BACKEND_GENERATE_PATH =
  process.env.VTON_BACKEND_GENERATE_PATH ?? "/vton/vton/generate";

export async function POST(request: Request) {
  try {
    const body = await request.text();

    const response = await fetch(`${BACKEND_BASE_URL}${BACKEND_GENERATE_PATH}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body,
      cache: "no-store",
    });

    const responseText = await response.text();

    return new NextResponse(responseText, {
      status: response.status,
      headers: {
        "Content-Type": response.headers.get("Content-Type") ?? "application/json",
      },
    });
  } catch (error) {
    const message =
      error instanceof Error
        ? error.message
        : "Unable to reach the VTON backend.";

    return NextResponse.json(
      { detail: message },
      {
        status: 502,
      },
    );
  }
}
