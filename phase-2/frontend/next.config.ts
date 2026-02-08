import type { NextConfig } from "next";
import createNextIntlPlugin from 'next-intl/plugin';

const withNextIntl = createNextIntlPlugin('./src/i18n/request.ts');

const nextConfig: NextConfig = {
  /* config options here */
  output: 'standalone',

  // Generate unique build IDs to bypass ALL caches
  generateBuildId: async () => {
    return `build-${Date.now()}-${Math.random().toString(36).substring(7)}`;
  },

  experimental: {
    // Reduce hydration errors from browser extensions
    optimizePackageImports: ["@radix-ui/react-dialog", "@radix-ui/react-slot"],
  },
  // Suppress hydration warnings in development
  reactStrictMode: true,
  // Handle browser extension conflicts
  compiler: {
    // TEMPORARILY DISABLE - Need console logs for debugging
    // removeConsole: process.env.NODE_ENV === "production",
  },
  // Turbopack configuration (Next.js 16+)
  turbopack: {
    // Empty config to silence Turbopack warnings
    // Custom configurations can be added here as needed
  },
};

export default withNextIntl(nextConfig);
