"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { FileText, Lightbulb, Loader2, Sparkles } from "lucide-react";
import { toast } from "sonner";
import { useSession } from "@/app/lib/auth-client";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { useLanguage } from "@/i18n/context/language-context";

export default function Dashboard() {
  const { data: session } = useSession();
  const { t, locale } = useLanguage();
  const router = useRouter();
  const [inputText, setInputText] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    if (!inputText.trim()) {
      toast.error(t("dashboard.validation.emptyInput"));
      return;
    }

    setIsSubmitting(true);

    try {
      const userId = session?.user?.id || session?.user?.email || "";
      const response = await fetch("/api/analyze-text", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ userId, text: inputText }),
      });

      if (response.ok) {
        toast.success(t("dashboard.toast.submitSuccess"));
        setInputText("");
        router.push(`/${locale}/tasks`);
      } else {
        const error = await response.json();
        toast.error(
          t("dashboard.toast.submitFailed", {
            message: error.error || t("dashboard.toast.unknownError"),
          }),
        );
      }
    } catch (error) {
      console.error("Submit error:", error);
      toast.error(t("dashboard.toast.networkFailed"));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="mx-auto max-w-5xl space-y-8 pt-12">
      <div className="pr-12 text-center">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          {t("dashboard.greeting", {
            name: session?.user?.name || t("dashboard.userFallback"),
          })}
        </h1>
        <p className="mt-1 text-gray-500 dark:text-gray-400">
          {t("dashboard.subtitle")}
        </p>
      </div>

      <Card className="-mx-4 border-0 bg-white shadow-lg dark:bg-gray-900">
        <CardHeader>
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600">
              <Sparkles className="h-5 w-5 text-white" />
            </div>
            <div>
              <CardTitle className="text-lg">{t("dashboard.cardTitle")}</CardTitle>
              <CardDescription>{t("dashboard.cardDescription")}</CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-5">
            <Textarea
              placeholder={t("dashboard.placeholder")}
              value={inputText}
              onChange={(event) => setInputText(event.target.value)}
              className="min-h-[200px] resize-none border-gray-200 text-base leading-relaxed focus-visible:ring-blue-500 dark:border-gray-700"
              disabled={isSubmitting}
            />

            <div className="flex items-center justify-between">
              <p className="text-sm text-gray-400">{t("dashboard.supportText")}</p>
              <div className="flex gap-3">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setInputText("")}
                  disabled={isSubmitting}
                >
                  {t("dashboard.clear")}
                </Button>
                <Button
                  type="submit"
                  disabled={isSubmitting || !inputText.trim()}
                  className="min-w-[140px] bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700"
                >
                  {isSubmitting ? (
                    <span className="flex items-center gap-2">
                      <Loader2 className="h-4 w-4 animate-spin" />
                      {t("dashboard.submitting")}
                    </span>
                  ) : (
                    <span className="flex items-center gap-2">
                      <FileText className="h-4 w-4" />
                      {t("dashboard.submit")}
                    </span>
                  )}
                </Button>
              </div>
            </div>
          </form>
        </CardContent>
      </Card>

      <Card className="mx-auto max-w-2xl border border-blue-100 bg-blue-50/50 dark:border-blue-900/30 dark:bg-blue-950/20">
        <CardContent className="py-4">
          <div className="flex gap-3">
            <Lightbulb className="mt-0.5 h-5 w-5 shrink-0 text-blue-500" />
            <div className="space-y-1 text-sm text-gray-600 dark:text-gray-400">
              <p className="font-medium text-gray-800 dark:text-gray-200">{t("dashboard.tips.title")}</p>
              <ul className="list-inside list-disc space-y-1">
                <li>{t("dashboard.tips.specific")}</li>
                <li>{t("dashboard.tips.downloadAndCheck")}</li>
                <li>{t("dashboard.tips.batchRules")}</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
