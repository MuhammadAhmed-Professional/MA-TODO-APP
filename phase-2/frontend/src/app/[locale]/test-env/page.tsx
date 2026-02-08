"use client";

import dynamic from "next/dynamic";

const TestEnvContent = dynamic(() => import("@/components/pages/TestEnvContent").then(m => ({ default: m.TestEnvContent })), {
  ssr: false,
});

export default function TestEnvPage() {
  return <TestEnvContent />;
}
