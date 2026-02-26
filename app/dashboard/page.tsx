"use client";

import { useSession, signOut } from "@/app/lib/auth-client";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

export default function Dashboard() {
  const { data: session, isPending } = useSession();
  const router = useRouter();

  const [inputText, setInputText] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (!isPending && !session?.user) {
      router.push("/sign-in");
    }
  }, [isPending, session?.user, router]);

  if (isPending) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-black">
        <svg className="animate-spin h-8 w-8 text-blue-600 mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"></path>
        </svg>
        <p className="text-lg text-gray-700 dark:text-gray-200 font-medium">Loading...</p>
      </div>
    );
  }

  if (!session?.user) {
    return null;
  }

  const handleSignOut = async () => {
    await signOut();
    router.push("/sign-in");
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!inputText.trim()) {
      alert("请输入IDS需求文本");
      return;
    }

    setIsSubmitting(true);

    try {
      const userId = session.user.id || session.user.email || "";

      const response = await fetch("/api/analyze-text", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          userId,
          text: inputText,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setInputText("");
        router.push("/tasks");
      } else {
        const error = await response.json();
        alert(`提交失败: ${error.error || "未知错误"}`);
      }
    } catch (error) {
      console.error("Submit error:", error);
      alert("提交失败，请检查网络连接");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-black">
      <div className="max-w-3xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-800 dark:text-gray-100">
              IDS Generator
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">
              从自然语言生成 IDS 规范文件
            </p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => router.push("/tasks")}>
              任务列表
            </Button>
            <Button variant="ghost" onClick={handleSignOut}>
              退出
            </Button>
          </div>
        </div>

        {/* Main Form */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Text Input */}
            <div className="space-y-2">
              <Label htmlFor="ids-text" className="text-base font-semibold">
                输入 IDS 需求描述
              </Label>
              <Textarea
                id="ids-text"
                placeholder="请用自然语言描述您的 IDS 规范要求，例如：&#10;&#10;• 所有 IfcWall 的防火等级必须为 A 级&#10;• 门的宽度必须大于 900mm&#10;• 楼板的承重必须大于 500kg/m²&#10;• 所有空间必须包含面积属性"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                className="min-h-[280px] text-base leading-relaxed"
                disabled={isSubmitting}
              />
              <p className="text-sm text-gray-500">
                支持中英文输入，系统将自动解析并生成符合 IDS 标准的 XML 文件
              </p>
            </div>

            {/* Submit Button */}
            <div className="flex justify-end gap-3">
              <Button
                type="button"
                variant="outline"
                onClick={() => setInputText("")}
                disabled={isSubmitting}
              >
                清空
              </Button>
              <Button
                type="submit"
                disabled={isSubmitting || !inputText.trim()}
                className="min-w-[140px]"
              >
                {isSubmitting ? (
                  <span className="flex items-center gap-2">
                    <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"></path>
                    </svg>
                    生成中...
                  </span>
                ) : (
                  "生成 IDS 文件"
                )}
              </Button>
            </div>
          </form>
        </div>

        {/* Footer hint */}
        <p className="text-center text-sm text-gray-400 dark:text-gray-500 mt-6">
          登录用户: {session.user.name || session.user.email}
        </p>
      </div>
    </div>
  );
}