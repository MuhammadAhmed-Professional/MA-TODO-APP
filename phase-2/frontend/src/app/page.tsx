/**
 * Landing Page
 *
 * Modern, beautiful landing page with hero section, features, and CTAs.
 * Built with gradient backgrounds, smooth animations, and responsive design.
 */

import Link from "next/link";
import { CheckCircle2, Zap, Shield, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-neutral-950 dark:via-neutral-900 dark:to-blue-950">
      {/* Navigation */}
      <nav className="sticky top-0 z-50 border-b border-neutral-200/50 bg-white/80 backdrop-blur-lg dark:border-neutral-800/50 dark:bg-neutral-900/80">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-2">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-blue-600 to-purple-600">
              <CheckCircle2 className="h-6 w-6 text-white" />
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              TaskFlow
            </span>
          </div>
          <div className="flex items-center gap-3">
            <Link href="/login">
              <Button variant="ghost" size="md">
                Login
              </Button>
            </Link>
            <Link href="/signup">
              <Button size="md">
                Get Started
              </Button>
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative overflow-hidden px-6 py-20 sm:py-32">
        {/* Gradient Orbs */}
        <div className="absolute -top-40 -right-40 h-80 w-80 rounded-full bg-purple-400/30 blur-3xl" />
        <div className="absolute -bottom-40 -left-40 h-80 w-80 rounded-full bg-blue-400/30 blur-3xl" />

        <div className="relative mx-auto max-w-4xl text-center">
          {/* Badge */}
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-blue-200 bg-blue-50 px-4 py-1.5 text-sm font-medium text-blue-700 dark:border-blue-900 dark:bg-blue-950 dark:text-blue-300">
            <Sparkles className="h-4 w-4" />
            New: Dark mode support
          </div>

          {/* Main Headline */}
          <h1 className="mb-6 text-5xl font-bold leading-tight tracking-tight text-neutral-900 sm:text-6xl md:text-7xl dark:text-white">
            Organize Your Tasks
            <br />
            <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              Effortlessly
            </span>
          </h1>

          {/* Subheadline */}
          <p className="mb-10 text-lg text-neutral-600 sm:text-xl dark:text-neutral-400">
            A modern, beautiful todo app with real-time sync, smart organization,
            and secure authentication. Stay productive, stay organized.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col items-center justify-center gap-4 sm:flex-row">
            <Link href="/signup">
              <Button size="lg" className="w-full sm:w-auto">
                Start for Free
              </Button>
            </Link>
            <Link href="/login">
              <Button variant="outline" size="lg" className="w-full sm:w-auto">
                Login
              </Button>
            </Link>
          </div>

          {/* Trust Badge */}
          <p className="mt-8 text-sm text-neutral-500 dark:text-neutral-500">
            No credit card required. Free forever.
          </p>
        </div>
      </section>

      {/* Features Section */}
      <section className="relative px-6 py-20">
        <div className="mx-auto max-w-6xl">
          <div className="mb-16 text-center">
            <h2 className="mb-4 text-3xl font-bold text-neutral-900 sm:text-4xl dark:text-white">
              Everything you need to stay organized
            </h2>
            <p className="text-lg text-neutral-600 dark:text-neutral-400">
              Powerful features designed to help you manage tasks efficiently
            </p>
          </div>

          <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
            {/* Feature 1 */}
            <Card className="group transition-all duration-300 hover:-translate-y-1">
              <CardHeader>
                <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-blue-100 text-blue-600 transition-colors group-hover:bg-blue-600 group-hover:text-white dark:bg-blue-900 dark:text-blue-300">
                  <Zap className="h-6 w-6" />
                </div>
                <CardTitle>Lightning Fast</CardTitle>
                <CardDescription>
                  Create, update, and complete tasks in milliseconds with our optimized interface
                </CardDescription>
              </CardHeader>
            </Card>

            {/* Feature 2 */}
            <Card className="group transition-all duration-300 hover:-translate-y-1">
              <CardHeader>
                <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-purple-100 text-purple-600 transition-colors group-hover:bg-purple-600 group-hover:text-white dark:bg-purple-900 dark:text-purple-300">
                  <Shield className="h-6 w-6" />
                </div>
                <CardTitle>Secure & Private</CardTitle>
                <CardDescription>
                  Your data is encrypted and protected with enterprise-grade security
                </CardDescription>
              </CardHeader>
            </Card>

            {/* Feature 3 */}
            <Card className="group transition-all duration-300 hover:-translate-y-1">
              <CardHeader>
                <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-green-100 text-green-600 transition-colors group-hover:bg-green-600 group-hover:text-white dark:bg-green-900 dark:text-green-300">
                  <CheckCircle2 className="h-6 w-6" />
                </div>
                <CardTitle>Smart Organization</CardTitle>
                <CardDescription>
                  Filter, sort, and search your tasks with powerful organization tools
                </CardDescription>
              </CardHeader>
            </Card>

            {/* Feature 4 */}
            <Card className="group transition-all duration-300 hover:-translate-y-1">
              <CardHeader>
                <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-amber-100 text-amber-600 transition-colors group-hover:bg-amber-600 group-hover:text-white dark:bg-amber-900 dark:text-amber-300">
                  <Sparkles className="h-6 w-6" />
                </div>
                <CardTitle>Beautiful Design</CardTitle>
                <CardDescription>
                  Enjoy a modern, clean interface that makes task management a pleasure
                </CardDescription>
              </CardHeader>
            </Card>

            {/* Feature 5 */}
            <Card className="group transition-all duration-300 hover:-translate-y-1">
              <CardHeader>
                <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-red-100 text-red-600 transition-colors group-hover:bg-red-600 group-hover:text-white dark:bg-red-900 dark:text-red-300">
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                  </svg>
                </div>
                <CardTitle>Dark Mode</CardTitle>
                <CardDescription>
                  Work comfortably day or night with automatic dark mode support
                </CardDescription>
              </CardHeader>
            </Card>

            {/* Feature 6 */}
            <Card className="group transition-all duration-300 hover:-translate-y-1">
              <CardHeader>
                <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-indigo-100 text-indigo-600 transition-colors group-hover:bg-indigo-600 group-hover:text-white dark:bg-indigo-900 dark:text-indigo-300">
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
                  </svg>
                </div>
                <CardTitle>Fully Responsive</CardTitle>
                <CardDescription>
                  Access your tasks anywhere, on any device with perfect mobile support
                </CardDescription>
              </CardHeader>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative px-6 py-20">
        <div className="mx-auto max-w-4xl">
          <Card className="border-2 border-blue-200 bg-gradient-to-br from-blue-50 to-purple-50 dark:border-blue-900 dark:from-blue-950 dark:to-purple-950">
            <CardHeader className="text-center">
              <CardTitle className="text-3xl sm:text-4xl">
                Ready to get organized?
              </CardTitle>
              <CardDescription className="text-base sm:text-lg">
                Join thousands of users who manage their tasks with TaskFlow
              </CardDescription>
            </CardHeader>
            <CardContent className="flex flex-col items-center justify-center gap-4 sm:flex-row">
              <Link href="/signup">
                <Button size="lg" className="w-full sm:w-auto">
                  Create Free Account
                </Button>
              </Link>
              <Link href="/login">
                <Button variant="outline" size="lg" className="w-full sm:w-auto">
                  Sign In
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-neutral-200 bg-white/50 backdrop-blur-lg dark:border-neutral-800 dark:bg-neutral-900/50">
        <div className="mx-auto max-w-7xl px-6 py-8">
          <div className="flex flex-col items-center justify-between gap-4 sm:flex-row">
            <div className="flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-blue-600 to-purple-600">
                <CheckCircle2 className="h-5 w-5 text-white" />
              </div>
              <span className="font-semibold text-neutral-900 dark:text-white">TaskFlow</span>
            </div>
            <p className="text-sm text-neutral-600 dark:text-neutral-400">
              2024 TaskFlow. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
