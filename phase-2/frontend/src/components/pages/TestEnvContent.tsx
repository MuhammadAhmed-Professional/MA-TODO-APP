"use client";

/**
 * Test page to check client-side environment variables
 * Access at: /test-env
 */

export function TestEnvContent() {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "NOT SET (using fallback)";
  const authUrl = process.env.NEXT_PUBLIC_AUTH_URL || "NOT SET (using fallback)";

  return (
    <div style={{ padding: "20px", fontFamily: "monospace" }}>
      <h1>Client-Side Environment Variables Test</h1>
      <div style={{ marginTop: "20px", padding: "10px", background: "#f0f0f0" }}>
        <p><strong>NEXT_PUBLIC_API_URL:</strong></p>
        <p style={{ color: apiUrl.includes("http://") ? "red" : "green" }}>
          {apiUrl}
        </p>
      </div>
      <div style={{ marginTop: "20px", padding: "10px", background: "#f0f0f0" }}>
        <p><strong>NEXT_PUBLIC_AUTH_URL:</strong></p>
        <p style={{ color: authUrl.includes("http://") ? "red" : "green" }}>
          {authUrl}
        </p>
      </div>
      <div style={{ marginTop: "20px", padding: "10px", background: "#f0f0f0" }}>
        <p><strong>From api.ts directly:</strong></p>
        <p style={{ wordBreak: "break-all" }}>
          Check browser console for API_BASE_URL value
        </p>
      </div>
      <script dangerouslySetInnerHTML={{__html: `
        console.log('CLIENT ENV CHECK:');
        console.log('NEXT_PUBLIC_API_URL:', process.env.NEXT_PUBLIC_API_URL || 'NOT SET');
        console.log('NEXT_PUBLIC_AUTH_URL:', process.env.NEXT_PUBLIC_AUTH_URL || 'NOT SET');
      `}} />
    </div>
  );
}
