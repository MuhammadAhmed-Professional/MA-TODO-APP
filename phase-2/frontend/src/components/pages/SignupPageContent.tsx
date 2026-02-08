/**
 * Signup Page
 *
 * Beautiful registration page with glassmorphism effects and modern design.
 * Integrates with Better Auth for secure user registration.
 */

"use client";

import { useState, FormEvent } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { signUp } from "@/lib/auth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { CheckCircle2, AlertCircle, Loader2, Check } from "lucide-react";
import type { TranslationValues } from "next-intl";

interface SignupPageContentProps {
  translations: (key: string, values?: TranslationValues) => string;
}

export function SignupPageContent({ translations: t }: SignupPageContentProps) {
  const router = useRouter();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  // Password strength indicators
  const passwordStrength = {
    hasMinLength: password.length >= 8,
    hasNumber: /\d/.test(password),
    hasSpecialChar: /[!@#$%^&*(),.?":{}|<>]/.test(password),
  };

  const isPasswordValid = Object.values(passwordStrength).every(Boolean);

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError("");

    // Validation
    if (!isPasswordValid) {
      setError("Please meet all password requirements");
      return;
    }

    setIsLoading(true);

    try {
      const result = await signUp({
        name,
        email,
        password,
      });

      if (result.error) {
        setError(t('signUpError') || "Signup failed. Please try again.");
        return;
      }

      // Success - redirect to dashboard
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "An unexpected error occurred");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-neutral-950 dark:via-neutral-900 dark:to-blue-950">
      {/* Gradient Orbs */}
      <div className="absolute -top-40 -right-40 h-80 w-80 rounded-full bg-purple-400/20 blur-3xl" />
      <div className="absolute -bottom-40 -left-40 h-80 w-80 rounded-full bg-blue-400/20 blur-3xl" />

      <div className="relative w-full max-w-md">
        {/* Logo */}
        <div className="mb-8 text-center">
          <Link href="/" className="inline-flex items-center gap-2">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-gradient-to-br from-blue-600 to-purple-600">
              <CheckCircle2 className="h-7 w-7 text-white" />
            </div>
            <span className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              TaskFlow
            </span>
          </Link>
        </div>

        {/* Signup Card with Glassmorphism */}
        <Card className="border-neutral-200/50 bg-white/80 backdrop-blur-xl shadow-2xl dark:border-neutral-800/50 dark:bg-neutral-900/80">
          <CardHeader className="space-y-1">
            <CardTitle className="text-2xl font-bold text-center">{t('createAccount')}</CardTitle>
            <CardDescription className="text-center">
              {t('getStarted')}
            </CardDescription>
          </CardHeader>

          <form onSubmit={handleSubmit}>
            <CardContent className="space-y-4">
              {/* Error Message */}
              {error && (
                <div className="flex items-start gap-3 rounded-lg bg-red-50 p-4 border border-red-200 dark:bg-red-950/50 dark:border-red-900">
                  <AlertCircle className="h-5 w-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
                  <p className="text-sm text-red-800 dark:text-red-200">{error}</p>
                </div>
              )}

              {/* Name Field */}
              <div className="space-y-2">
                <Label htmlFor="name">{t('fullName')}</Label>
                <Input
                  id="name"
                  name="name"
                  type="text"
                  autoComplete="name"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="John Doe"
                  disabled={isLoading}
                />
              </div>

              {/* Email Field */}
              <div className="space-y-2">
                <Label htmlFor="email">{t('email')}</Label>
                <Input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  disabled={isLoading}
                />
              </div>

              {/* Password Field */}
              <div className="space-y-2">
                <Label htmlFor="password">{t('password')}</Label>
                <Input
                  id="password"
                  name="password"
                  type="password"
                  autoComplete="new-password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  disabled={isLoading}
                />

                {/* Password Requirements */}
                {password && (
                  <div className="space-y-2 mt-3 p-3 rounded-lg bg-neutral-50 dark:bg-neutral-800/50">
                    <p className="text-xs font-medium text-neutral-700 dark:text-neutral-300 mb-2">
                      Password must contain:
                    </p>
                    <div className="space-y-1.5">
                      <div className="flex items-center gap-2">
                        <div
                          className={`h-4 w-4 rounded-full flex items-center justify-center ${
                            passwordStrength.hasMinLength
                              ? "bg-green-500"
                              : "bg-neutral-300 dark:bg-neutral-700"
                          }`}
                        >
                          {passwordStrength.hasMinLength && (
                            <Check className="h-3 w-3 text-white" />
                          )}
                        </div>
                        <span
                          className={`text-xs ${
                            passwordStrength.hasMinLength
                              ? "text-green-700 dark:text-green-400"
                              : "text-neutral-600 dark:text-neutral-400"
                          }`}
                        >
                          At least 8 characters
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div
                          className={`h-4 w-4 rounded-full flex items-center justify-center ${
                            passwordStrength.hasNumber
                              ? "bg-green-500"
                              : "bg-neutral-300 dark:bg-neutral-700"
                          }`}
                        >
                          {passwordStrength.hasNumber && (
                            <Check className="h-3 w-3 text-white" />
                          )}
                        </div>
                        <span
                          className={`text-xs ${
                            passwordStrength.hasNumber
                              ? "text-green-700 dark:text-green-400"
                              : "text-neutral-600 dark:text-neutral-400"
                          }`}
                        >
                          One number
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div
                          className={`h-4 w-4 rounded-full flex items-center justify-center ${
                            passwordStrength.hasSpecialChar
                              ? "bg-green-500"
                              : "bg-neutral-300 dark:bg-neutral-700"
                          }`}
                        >
                          {passwordStrength.hasSpecialChar && (
                            <Check className="h-3 w-3 text-white" />
                          )}
                        </div>
                        <span
                          className={`text-xs ${
                            passwordStrength.hasSpecialChar
                              ? "text-green-700 dark:text-green-400"
                              : "text-neutral-600 dark:text-neutral-400"
                          }`}
                        >
                          One special character
                        </span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </CardContent>

            <CardFooter className="flex flex-col space-y-4">
              {/* Submit Button */}
              <Button
                type="submit"
                disabled={isLoading || !isPasswordValid}
                className="w-full"
                size="lg"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    {t('creatingAccount')}
                  </>
                ) : (
                  t('createAccount')
                )}
              </Button>

              {/* Divider */}
              <div className="relative w-full">
                <div className="absolute inset-0 flex items-center">
                  <span className="w-full border-t border-neutral-300 dark:border-neutral-700" />
                </div>
                <div className="relative flex justify-center text-xs uppercase">
                  <span className="bg-white px-2 text-neutral-500 dark:bg-neutral-900 dark:text-neutral-400">
                    {t('or')}
                  </span>
                </div>
              </div>

              {/* Social Signup (UI only for now) */}
              <Button
                type="button"
                variant="outline"
                className="w-full"
                size="lg"
                disabled
              >
                <svg className="mr-2 h-5 w-5" viewBox="0 0 24 24">
                  <path
                    d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                    fill="#4285F4"
                  />
                  <path
                    d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                    fill="#34A853"
                  />
                  <path
                    d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                    fill="#FBBC05"
                  />
                  <path
                    d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                    fill="#EA4335"
                  />
                </svg>
                {t('continueWithGoogle')}
              </Button>

              {/* Terms */}
              <p className="text-center text-xs text-neutral-500 dark:text-neutral-400 px-4">
                {t('agreeToTerms')}{" "}
                <Link href="/terms" className="underline hover:text-neutral-700 dark:hover:text-neutral-300">
                  {t('termsOfService')}
                </Link>{" "}
                {t('and')}{" "}
                <Link href="/privacy" className="underline hover:text-neutral-700 dark:hover:text-neutral-300">
                  {t('privacyPolicy')}
                </Link>
              </p>

              {/* Login Link */}
              <p className="text-center text-sm text-neutral-600 dark:text-neutral-400">
                {t('hasAccount')}{" "}
                <Link
                  href="/login"
                  className="font-semibold text-blue-600 hover:text-blue-500 dark:text-blue-400"
                >
                  {t('signIn')}
                </Link>
              </p>
            </CardFooter>
          </form>
        </Card>

        {/* Footer */}
        <p className="mt-8 text-center text-sm text-neutral-500 dark:text-neutral-400">
          {t('protectedBySecurity')}
        </p>
      </div>
    </div>
  );
}
