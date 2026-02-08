/**
 * API Response Type Definitions
 *
 * Common response types for API interactions.
 */

export interface APIError {
  detail: string;
  status?: number;
}

export interface HealthResponse {
  status: "healthy" | "degraded";
  database?: "connected" | "disconnected";
  version?: string;
}
