/**
 * k6 Load Test for Phase III Chat API
 *
 * Simulates realistic chat usage patterns:
 * - User authentication
 * - Conversation creation
 * - Message sending and receiving
 * - Conversation deletion
 *
 * Run with:
 * k6 run tests/load/chat_load_test.js
 *
 * With options:
 * k6 run -e BASE_URL=http://localhost:8000 \
 *        -e DURATION=30s \
 *        -e VUS=50 \
 *        tests/load/chat_load_test.js
 */

import http from "k6/http";
import { check, group, sleep } from "k6";

// Configuration
export const options = {
  stages: [
    { duration: "30s", target: 20 },   // Ramp-up to 20 users
    { duration: "1m30s", target: 50 }, // Ramp-up to 50 users
    { duration: "20s", target: 0 },    // Ramp-down to 0 users
  ],
  thresholds: {
    http_req_duration: ["p(95)<3000"],  // 95% of requests < 3 seconds
    http_req_failed: ["rate<0.1"],      // Error rate < 10%
  },
};

const BASE_URL = __ENV.BASE_URL || "http://localhost:8000";
const API_URL = `${BASE_URL}/api`;

// Test user credentials
const testUser = {
  email: `test-load-${__VU}-${__ITER}@example.com`,
  password: "Test@123456",
};

export default function () {
  let authToken = null;
  let conversationId = null;

  // ============================================================
  // 1. AUTHENTICATION TEST
  // ============================================================
  group("Authentication", function () {
    // Sign up new test user
    let signupRes = http.post(
      `${API_URL}/auth/signup`,
      JSON.stringify({
        email: testUser.email,
        password: testUser.password,
        name: `Load Test User ${__VU}`,
      }),
      {
        headers: {
          "Content-Type": "application/json",
        },
      }
    );

    check(signupRes, {
      "signup status is 200": (r) => r.status === 200 || r.status === 409, // 409 if already exists
      "signup returns user data": (r) => {
        try {
          const body = JSON.parse(r.body);
          return body.user && body.user.id;
        } catch {
          return false;
        }
      },
    });

    sleep(0.5);

    // Sign in
    let signinRes = http.post(
      `${API_URL}/auth/signin`,
      JSON.stringify({
        email: testUser.email,
        password: testUser.password,
      }),
      {
        headers: {
          "Content-Type": "application/json",
        },
      }
    );

    check(signinRes, {
      "signin status is 200": (r) => r.status === 200,
      "signin returns session": (r) => {
        try {
          const body = JSON.parse(r.body);
          return body.session && body.session.token;
        } catch {
          return false;
        }
      },
    });

    try {
      const signinBody = JSON.parse(signinRes.body);
      authToken = signinBody.session.token;
    } catch {
      console.error("Failed to extract auth token");
    }
  });

  if (!authToken) {
    console.warn("No auth token, skipping remaining tests");
    return;
  }

  // ============================================================
  // 2. CONVERSATION MANAGEMENT TEST
  // ============================================================
  group("Conversation Management", function () {
    // Create conversation
    let createRes = http.post(
      `${API_URL}/chat/conversations`,
      JSON.stringify({
        title: `Load Test Conversation ${__ITER}`,
      }),
      {
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${authToken}`,
        },
        cookies: {
          auth_token: authToken,
        },
      }
    );

    check(createRes, {
      "create conversation status is 200": (r) => r.status === 200,
      "create returns conversation id": (r) => {
        try {
          const body = JSON.parse(r.body);
          return body.id && body.id.length > 0;
        } catch {
          return false;
        }
      },
    });

    try {
      const createBody = JSON.parse(createRes.body);
      conversationId = createBody.id;
    } catch {
      console.error("Failed to extract conversation ID");
    }

    sleep(0.5);

    // List conversations
    let listRes = http.get(`${API_URL}/chat/conversations`, {
      headers: {
        Authorization: `Bearer ${authToken}`,
      },
      cookies: {
        auth_token: authToken,
      },
    });

    check(listRes, {
      "list conversations status is 200": (r) => r.status === 200,
      "list returns array": (r) => {
        try {
          const body = JSON.parse(r.body);
          return Array.isArray(body.conversations);
        } catch {
          return false;
        }
      },
    });

    sleep(0.5);

    // Get single conversation
    if (conversationId) {
      let getRes = http.get(`${API_URL}/chat/conversations/${conversationId}`, {
        headers: {
          Authorization: `Bearer ${authToken}`,
        },
        cookies: {
          auth_token: authToken,
        },
      });

      check(getRes, {
        "get conversation status is 200": (r) => r.status === 200,
        "get returns conversation": (r) => {
          try {
            const body = JSON.parse(r.body);
            return body.id === conversationId;
          } catch {
            return false;
          }
        },
      });

      sleep(0.5);
    }
  });

  // ============================================================
  // 3. MESSAGE HANDLING TEST
  // ============================================================
  if (conversationId) {
    group("Message Handling", function () {
      // Send message
      let sendRes = http.post(
        `${API_URL}/chat/conversations/${conversationId}/messages`,
        JSON.stringify({
          content: `Load test message from VU ${__VU} iteration ${__ITER}`,
        }),
        {
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${authToken}`,
          },
          cookies: {
            auth_token: authToken,
          },
        }
      );

      check(sendRes, {
        "send message status is 200": (r) => r.status === 200,
        "send returns messages": (r) => {
          try {
            const body = JSON.parse(r.body);
            return body.user_message && body.assistant_message;
          } catch {
            return false;
          }
        },
      });

      sleep(1); // Wait for API response

      // Get messages
      let getMessagesRes = http.get(
        `${API_URL}/chat/conversations/${conversationId}/messages`,
        {
          headers: {
            Authorization: `Bearer ${authToken}`,
          },
          cookies: {
            auth_token: authToken,
          },
        }
      );

      check(getMessagesRes, {
        "get messages status is 200": (r) => r.status === 200,
        "get messages returns array": (r) => {
          try {
            const body = JSON.parse(r.body);
            return Array.isArray(body.messages);
          } catch {
            return false;
          }
        },
      });

      sleep(0.5);
    });
  }

  // ============================================================
  // 4. CLEANUP TEST
  // ============================================================
  if (conversationId) {
    group("Cleanup", function () {
      let deleteRes = http.del(
        `${API_URL}/chat/conversations/${conversationId}`,
        null,
        {
          headers: {
            Authorization: `Bearer ${authToken}`,
          },
          cookies: {
            auth_token: authToken,
          },
        }
      );

      check(deleteRes, {
        "delete conversation status is 200": (r) => r.status === 200 || r.status === 204,
      });

      sleep(0.5);
    });
  }

  // Random think time between requests
  sleep(__ENV.THINK_TIME ? parseFloat(__ENV.THINK_TIME) : 1);
}
