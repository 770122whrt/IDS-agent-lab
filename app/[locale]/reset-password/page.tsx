"use client";

import { Suspense, useEffect, useState } from "react";
import { ArrowLeft, Loader2, Lock, Mail } from "lucide-react";
import { FaLock } from "react-icons/fa";
import { toast } from "sonner";
import { useRouter, useSearchParams } from "next/navigation";
import { resetPassword, sendResetPasswordEmail } from "@/app/lib/auth-client";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { LanguageToggle } from "@/components/ui/language-toggle";
import { useLanguage } from "@/i18n/context/language-context";
import { cn } from "@/lib/utils";

function RequestResetStep() {
  const { t, locale } = useLanguage();
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleSubmit = async () => {
    if (!email) {
      toast.error(t("auth.reset.missingEmail"));
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
            toast.success(t("auth.reset.sendSuccess"));
          },
        },
      });

      if (error) {
        toast.error(error.message);
      }
    } catch {
      toast.error(t("auth.reset.sendFailed"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <CardHeader className="space-y-2 text-center">
        <CardTitle className="text-xl font-semibold md:text-2xl">{t("auth.reset.requestTitle")}</CardTitle>
        <CardDescription className="text-sm text-muted-foreground md:text-base">
          {t("auth.reset.requestDescription")}
        </CardDescription>
      </CardHeader>

      <CardContent className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="email">{t("auth.signIn.email")}</Label>
          <div className="relative">
            <Mail className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              id="email"
              type="email"
              placeholder="m@example.com"
              className="pl-10"
              required
              value={email}
              onChange={(event) => setEmail(event.target.value)}
            />
          </div>
        </div>

        <Button className="flex w-full items-center justify-center gap-2" disabled={loading} onClick={handleSubmit}>
          {loading ? (
            <Loader2 size={16} className="animate-spin" />
          ) : (
            <>
              <FaLock className="h-4 w-4" />
              {t("auth.reset.sendLink")}
            </>
          )}
        </Button>

        <div className="text-center">
          <Button variant="link" className="text-sm" onClick={() => router.push(`/${locale}/sign-in`)}>
            <ArrowLeft className="mr-1 h-4 w-4" />
            {t("auth.reset.backToSignIn")}
          </Button>
        </div>
      </CardContent>

      <CardFooter className="flex items-center justify-center border-t py-4 text-center text-xs text-neutral-500">
        {t("auth.securedBy")} <span className="ml-1 font-medium text-orange-400">better-auth</span>
      </CardFooter>
    </>
  );
}

function ResetPasswordStep() {
  const { t, locale } = useLanguage();
  const searchParams = useSearchParams();
  const token = searchParams.get("token");
  const email = searchParams.get("email");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  useEffect(() => {
    if (!token || !email) {
      toast.error(t("auth.reset.invalidLink"));
      router.push(`/${locale}/reset-password`);
    }
  }, [token, email, router, locale, t]);

  const handleSubmit = async () => {
    if (!password || !confirmPassword) {
      toast.error(t("auth.reset.missingFields"));
      return;
    }

    if (password !== confirmPassword) {
      toast.error(t("auth.reset.passwordMismatch"));
      return;
    }

    if (password.length < 8) {
      toast.error(t("auth.reset.passwordTooShort"));
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
            toast.success(t("auth.reset.success"));
            router.push(`/${locale}/sign-in`);
          },
        },
      });

      if (error) {
        toast.error(error.message);
      }
    } catch {
      toast.error(t("auth.reset.failed"));
    } finally {
      setLoading(false);
    }
  };

  if (!token || !email) {
    return null;
  }

  return (
    <>
      <CardHeader className="space-y-2 text-center">
        <CardTitle className="text-xl font-semibold md:text-2xl">{t("auth.reset.newPasswordTitle")}</CardTitle>
        <CardDescription className="text-sm text-muted-foreground md:text-base">
          {t("auth.reset.newPasswordDescription")}
        </CardDescription>
      </CardHeader>

      <CardContent className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="email">{t("auth.signIn.email")}</Label>
          <Input id="email" type="email" value={email} disabled className="bg-muted" />
        </div>

        <div className="space-y-2">
          <Label htmlFor="password">{t("auth.reset.newPassword")}</Label>
          <div className="relative">
            <Lock className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              id="password"
              type="password"
              placeholder="********"
              className="pl-10"
              required
              value={password}
              onChange={(event) => setPassword(event.target.value)}
            />
          </div>
        </div>

        <div className="space-y-2">
          <Label htmlFor="confirm_password">{t("auth.reset.confirmPassword")}</Label>
          <div className="relative">
            <Lock className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              id="confirm_password"
              type="password"
              placeholder="********"
              className="pl-10"
              required
              value={confirmPassword}
              onChange={(event) => setConfirmPassword(event.target.value)}
            />
          </div>
        </div>

        <Button className="flex w-full items-center justify-center gap-2" disabled={loading} onClick={handleSubmit}>
          {loading ? (
            <Loader2 size={16} className="animate-spin" />
          ) : (
            <>
              <FaLock className="h-4 w-4" />
              {t("auth.reset.submit")}
            </>
          )}
        </Button>

        <div className="text-center">
          <Button variant="link" className="text-sm" onClick={() => router.push(`/${locale}/sign-in`)}>
            <ArrowLeft className="mr-1 h-4 w-4" />
            {t("auth.reset.backToSignIn")}
          </Button>
        </div>
      </CardContent>

      <CardFooter className="flex items-center justify-center border-t py-4 text-center text-xs text-neutral-500">
        {t("auth.securedBy")} <span className="ml-1 font-medium text-orange-400">better-auth</span>
      </CardFooter>
    </>
  );
}

function ResetPasswordContent() {
  const searchParams = useSearchParams();
  const token = searchParams.get("token");
  const isResetStep = !!token;

  return (
    <div
      className={cn(
        "flex min-h-screen w-full flex-col items-center justify-center px-4",
        "bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-black",
      )}
    >
      <div className="absolute right-6 top-6">
        <LanguageToggle />
      </div>
      <Card
        className={cn(
          "w-full sm:w-[380px] md:w-[420px]",
          "rounded-2xl border border-neutral-200 bg-white shadow-lg transition-all duration-300 dark:border-neutral-800 dark:bg-neutral-900",
        )}
      >
        {isResetStep ? <ResetPasswordStep /> : <RequestResetStep />}
      </Card>
    </div>
  );
}

export default function ResetPassword() {
  return (
    <Suspense
      fallback={
        <div className="flex min-h-screen items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin" />
        </div>
      }
    >
      <ResetPasswordContent />
    </Suspense>
  );
}
