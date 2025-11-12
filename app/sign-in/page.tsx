"use client";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
  CardFooter,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { useState } from "react";
import { Loader2 } from "lucide-react";
import { signIn } from "@/app/lib/auth-client";
import Link from "next/link";
import { cn } from "@/lib/utils";
import { FaGithub, FaGoogle } from "react-icons/fa";

export default function SignIn() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);

  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center min-h-screen w-full px-4",
        "bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-black"
      )}
    >
      <Card
        className={cn(
          "w-full sm:w-[380px] md:w-[420px] lg:w-[460px] xl:w-[500px]",
          "shadow-lg rounded-2xl bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 transition-all duration-300"
        )}
      >
        <CardHeader className="text-center space-y-2">
          <CardTitle className="text-xl md:text-2xl font-semibold">Sign In</CardTitle>
          <CardDescription className="text-sm md:text-base text-muted-foreground">
            Enter your credentials to access your account
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-4">
          {/* Email */}
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              placeholder="m@example.com"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          {/* Password */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label htmlFor="password">Password</Label>
              <Link href="#" className="text-sm text-blue-600 hover:underline">
                Forgot password?
              </Link>
            </div>
            <Input
              id="password"
              type="password"
              placeholder="••••••••"
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          {/* Remember Me */}
          <div className="flex items-center gap-2">
            <Checkbox id="remember" checked={rememberMe} onCheckedChange={setRememberMe} />
            <Label htmlFor="remember" className="text-sm">
              Remember me
            </Label>
          </div>

          {/* Email Login Button */}
          <Button
            className="w-full mt-2"
            disabled={loading}
            onClick={async () => {
              await signIn.email(
                { email, password },
                {
                  onRequest: () => setLoading(true),
                  onResponse: () => setLoading(false),
                }
              );
            }}
          >
            {loading ? <Loader2 size={16} className="animate-spin" /> : "Login"}
          </Button>

          {/* Social Login */}
          <div className="flex flex-col gap-2 pt-2">
            <Button
              variant="outline"
              className="w-full gap-2"
              disabled={loading}
              onClick={async () => {
                await signIn.social(
                  { provider: "github", callbackURL: "/dashboard" },
                  { onRequest: () => setLoading(true), onResponse: () => setLoading(false) }
                );
              }}
            >
              <FaGithub className="w-4 h-4 text-neutral-700 dark:text-neutral-200" />
              Sign in with GitHub
            </Button>

            <Button
              variant="outline"
              className="w-full gap-2"
              disabled={loading}
              onClick={async () => {
                await signIn.social(
                  { provider: "google", callbackURL: "/dashboard" },
                  { onRequest: () => setLoading(true), onResponse: () => setLoading(false) }
                );
              }}
            >
              <FaGoogle className="w-4 h-4 text-red-500 dark:text-red-400" />
              Sign in with Google
            </Button>
          </div>
        </CardContent>

        {/* Footer */}
        <CardFooter className="border-t py-4 flex justify-center items-center text-center text-xs text-neutral-500">
          built with{" "}
          <Link
            href="https://better-auth.com"
            target="_blank"
            className="underline ml-1 text-neutral-600 dark:text-neutral-300"
          >
            better-auth
          </Link>
        </CardFooter>
      </Card>
    </div>
  );
}
