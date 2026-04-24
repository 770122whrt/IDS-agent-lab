"use client";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardDescription,
  CardFooter,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useState, useEffect, Suspense } from "react";
import { Loader2, Lock, Mail, ArrowLeft } from "lucide-react";
import { resetPassword, sendResetPasswordEmail } from "@/app/lib/auth-client";
import { toast } from "sonner";
import { useRouter, useSearchParams } from "next/navigation";
import { cn } from "@/lib/utils";
import { FaLock } from "react-icons/fa";

// Step 1: Request reset email
function RequestResetStep() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleSubmit = async () => {
    if (!email) {
      toast.error("Please enter your email address");
      return;
    }

    setLoading(true);
    try {
      const { error } = await sendResetPasswordEmail({
        email,
        fetchOptions: {
          onRequest: () => setLoading(true),
          onResponse: () => setLoading(false),
          onError: (ctx) => {
            toast.error(ctx.error.message);
          },
          onSuccess: () => {
            toast.success("Password reset link sent! Check your email.");
          },
        },
      });

      if (error) {
        toast.error(error.message);
      }
    } catch (err) {
      toast.error("Failed to send reset email");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <CardHeader className="text-center space-y-2">
        <CardTitle className="text-xl md:text-2xl font-semibold">
          Reset Password
        </CardTitle>
        <CardDescription className="text-sm md:text-base text-muted-foreground">
          Enter your email address and we will send you a reset link
        </CardDescription>
      </CardHeader>

      <CardContent className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="email">Email</Label>
          <div className="relative">
            <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              id="email"
              type="email"
              placeholder="m@example.com"
              className="pl-10"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>
        </div>

        <Button
          className="w-full flex items-center justify-center gap-2"
          disabled={loading}
          onClick={handleSubmit}
        >
          {loading ? (
            <Loader2 size={16} className="animate-spin" />
          ) : (
            <>
              <FaLock className="w-4 h-4" />
              Send Reset Link
            </>
          )}
        </Button>

        <div className="text-center">
          <Button
            variant="link"
            className="text-sm"
            onClick={() => router.push("/sign-in")}
          >
            <ArrowLeft className="w-4 h-4 mr-1" />
            Back to Sign In
          </Button>
        </div>
      </CardContent>

      <CardFooter className="border-t py-4 flex justify-center items-center text-center text-xs text-neutral-500">
        Secured by{" "}
        <span className="text-orange-400 font-medium ml-1">better-auth</span>
      </CardFooter>
    </>
  );
}

// Step 2: Set new password (after clicking reset link)
function ResetPasswordStep() {
  const searchParams = useSearchParams();
  const token = searchParams.get("token");
  const email = searchParams.get("email");

  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  useEffect(() => {
    if (!token || !email) {
      toast.error("Invalid reset link");
      router.push("/forgot-password");
    }
  }, [token, email, router]);

  const handleSubmit = async () => {
    if (!password || !confirmPassword) {
      toast.error("Please fill in all fields");
      return;
    }

    if (password !== confirmPassword) {
      toast.error("Passwords do not match");
      return;
    }

    if (password.length < 8) {
      toast.error("Password must be at least 8 characters");
      return;
    }

    setLoading(true);
    try {
      const { error } = await resetPassword({
        token: token!,
        newPassword: password,
        fetchOptions: {
          onRequest: () => setLoading(true),
          onResponse: () => setLoading(false),
          onError: (ctx) => {
            toast.error(ctx.error.message);
          },
          onSuccess: () => {
            toast.success("Password reset successfully!");
            router.push("/sign-in");
          },
        },
      });

      if (error) {
        toast.error(error.message);
      }
    } catch (err) {
      toast.error("Failed to reset password");
    } finally {
      setLoading(false);
    }
  };

  if (!token || !email) {
    return null;
  }

  return (
    <>
      <CardHeader className="text-center space-y-2">
        <CardTitle className="text-xl md:text-2xl font-semibold">
          Set New Password
        </CardTitle>
        <CardDescription className="text-sm md:text-base text-muted-foreground">
          Enter your new password below
        </CardDescription>
      </CardHeader>

      <CardContent className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="email">Email</Label>
          <Input
            id="email"
            type="email"
            value={email}
            disabled
            className="bg-muted"
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="password">New Password</Label>
          <div className="relative">
            <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              id="password"
              type="password"
              placeholder="••••••••"
              className="pl-10"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>
        </div>

        <div className="space-y-2">
          <Label htmlFor="confirm_password">Confirm Password</Label>
          <div className="relative">
            <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              id="confirm_password"
              type="password"
              placeholder="••••••••"
              className="pl-10"
              required
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
            />
          </div>
        </div>

        <Button
          className="w-full flex items-center justify-center gap-2"
          disabled={loading}
          onClick={handleSubmit}
        >
          {loading ? (
            <Loader2 size={16} className="animate-spin" />
          ) : (
            <>
              <FaLock className="w-4 h-4" />
              Reset Password
            </>
          )}
        </Button>

        <div className="text-center">
          <Button
            variant="link"
            className="text-sm"
            onClick={() => router.push("/sign-in")}
          >
            <ArrowLeft className="w-4 h-4 mr-1" />
            Back to Sign In
          </Button>
        </div>
      </CardContent>

      <CardFooter className="border-t py-4 flex justify-center items-center text-center text-xs text-neutral-500">
        Secured by{" "}
        <span className="text-orange-400 font-medium ml-1">better-auth</span>
      </CardFooter>
    </>
  );
}

// Main component with Suspense
function ResetPasswordContent() {
  const searchParams = useSearchParams();
  const token = searchParams.get("token");

  // If token exists, show reset password form
  // Otherwise, show request reset email form
  const isResetStep = !!token;

  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center min-h-screen w-full px-4",
        "bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-black"
      )}
    >
      <Card
        className={cn(
          "w-full sm:w-[380px] md:w-[420px]",
          "shadow-lg rounded-2xl bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 transition-all duration-300"
        )}
      >
        {isResetStep ? <ResetPasswordStep /> : <RequestResetStep />}
      </Card>
    </div>
  );
}

export default function ResetPassword() {
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="w-8 h-8 animate-spin" />
      </div>
    }>
      <ResetPasswordContent />
    </Suspense>
  );
}
