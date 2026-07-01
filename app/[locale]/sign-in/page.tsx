"use client";

import Link from "next/link";
import { useState } from "react";
import { Loader2 } from "lucide-react";
import { FaGithub, FaGoogle } from "react-icons/fa";
import { toast } from "sonner";
import { useRouter } from "next/navigation";
import { signIn } from "@/app/lib/auth-client";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { LanguageToggle } from "@/components/ui/language-toggle";
import { useLanguage } from "@/i18n/context/language-context";
import { cn } from "@/lib/utils";

export default function SignIn() {
  const router = useRouter();
  const { t, locale } = useLanguage();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [error, setError] = useState("");

  const dashboardPath = `/${locale}/dashboard`;

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
          "w-full sm:w-[380px] md:w-[420px] lg:w-[460px] xl:w-[500px]",
          "rounded-2xl border border-neutral-200 bg-white shadow-lg transition-all duration-300 dark:border-neutral-800 dark:bg-neutral-900",
        )}
      >
        <CardHeader className="space-y-2 text-center">
          <CardTitle className="text-xl font-semibold md:text-2xl">{t("auth.signIn.title")}</CardTitle>
          <CardDescription className="text-sm text-muted-foreground md:text-base">
            {t("auth.signIn.description")}
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-4">
          {error && (
            <div className="mb-2 text-center text-sm font-medium text-red-600">
              {error === "Invalid password" ? t("auth.signIn.errors.invalidPassword") : error}
            </div>
          )}

          <div className="space-y-2">
            <Label htmlFor="email">{t("auth.signIn.email")}</Label>
            <Input
              id="email"
              type="email"
              placeholder="m@example.com"
              required
              value={email}
              onChange={(event) => setEmail(event.target.value)}
            />
          </div>

          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label htmlFor="password">{t("auth.signIn.password")}</Label>
              <Link href={`/${locale}/reset-password`} className="text-sm text-blue-600 hover:underline">
                {t("auth.signIn.forgotPassword")}
              </Link>
            </div>
            <Input
              id="password"
              type="password"
              placeholder="********"
              autoComplete="current-password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
            />
          </div>

          <div className="flex items-center gap-2">
            <Checkbox id="remember" checked={rememberMe} onCheckedChange={(checked) => setRememberMe(checked === true)} />
            <Label htmlFor="remember" className="text-sm">
              {t("auth.signIn.rememberMe")}
            </Label>
          </div>

          <Button
            className="mt-2 w-full"
            disabled={loading}
            onClick={async () => {
              setError("");
              if (!email || !password) {
                const message = t("auth.signIn.errors.missingCredentials");
                toast.error(message);
                setError(message);
                return;
              }

              await signIn.email(
                {
                  email,
                  password,
                  callbackURL: dashboardPath,
                },
                {
                  onRequest: () => setLoading(true),
                  onResponse: () => setLoading(false),
                  onError: (ctx) => {
                    const message = ctx.error.message || ctx.error.statusText || t("auth.signIn.errors.failed");
                    toast.error(message);
                    setError(message);
                  },
                  onSuccess: (ctx) => {
                    console.log("Logged in as:", ctx.data?.user?.email);
                    toast.success(t("auth.signIn.success"));
                    router.push(dashboardPath);
                  },
                },
              );
            }}
          >
            {loading ? <Loader2 size={16} className="animate-spin" /> : t("auth.signIn.submit")}
          </Button>

          <div className="flex flex-col gap-2 pt-2">
            <Button
              variant="outline"
              className="w-full gap-2"
              disabled={loading}
              onClick={async () => {
                await signIn.social(
                  { provider: "github", callbackURL: dashboardPath },
                  {
                    onRequest: () => setLoading(true),
                    onResponse: () => setLoading(false),
                    onError: (ctx) => {
                      toast.error(ctx.error.message);
                    },
                  },
                );
              }}
            >
              <FaGithub className="h-4 w-4 text-neutral-700 dark:text-neutral-200" />
              {t("auth.signIn.github")}
            </Button>

            <Button
              variant="outline"
              className="w-full gap-2"
              disabled={loading}
              onClick={async () => {
                await signIn.social(
                  { provider: "google", callbackURL: dashboardPath },
                  {
                    onRequest: () => setLoading(true),
                    onResponse: () => setLoading(false),
                    onError: (ctx) => {
                      toast.error(ctx.error.message);
                    },
                  },
                );
              }}
            >
              <FaGoogle className="h-4 w-4 text-red-500 dark:text-red-400" />
              {t("auth.signIn.google")}
            </Button>
          </div>
        </CardContent>

        <CardFooter className="flex items-center justify-center border-t py-4 text-center text-xs text-neutral-500">
          {t("auth.builtWith")}{" "}
          <Link
            href="https://better-auth.com"
            target="_blank"
            className="ml-1 underline text-neutral-600 dark:text-neutral-300"
          >
            better-auth
          </Link>
        </CardFooter>
      </Card>
    </div>
  );
}
