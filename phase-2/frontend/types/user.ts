/**
 * User Type Definitions
 *
 * These types MUST match the backend UserResponse schema exactly.
 * See: backend/src/models/user.py
 */

export interface User {
  id: string; // UUID
  email: string;
  name: string;
  created_at: string; // ISO 8601 timestamp
  updated_at: string; // ISO 8601 timestamp
}

export interface UserSignup {
  email: string;
  name: string;
  password: string;
}

export interface UserLogin {
  email: string;
  password: string;
}

export interface AuthResponse {
  id: string;
  email: string;
  name: string;
  created_at: string;
  updated_at: string;
}
