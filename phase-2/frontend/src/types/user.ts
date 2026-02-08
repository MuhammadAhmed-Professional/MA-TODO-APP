/**
 * User Type Definitions
 *
 * MUST match backend UserResponse model exactly.
 * See: backend/src/models/user.py
 */

/**
 * User model (matches backend UserResponse)
 */
export interface User {
  id: string; // UUID
  email: string;
  name: string;
  created_at: string; // ISO 8601 datetime
  updated_at: string; // ISO 8601 datetime
}

/**
 * User creation payload (signup)
 */
export interface UserCreate {
  email: string;
  name: string;
  password: string;
}

/**
 * User login payload
 */
export interface UserLogin {
  email: string;
  password: string;
}

/**
 * Auth session (returned by Better Auth)
 */
export interface Session {
  user: User;
  session: {
    token: string;
    expiresAt: string; // ISO 8601 datetime
  };
}
