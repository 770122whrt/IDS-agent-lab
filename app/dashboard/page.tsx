"use client";

import { useSession, signOut } from "@/app/lib/auth-client";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

export default function Dashboard() {
  const { data: session, isPending } = useSession();
  const router = useRouter();

  const [inputText, setInputText] = useState("");
  const [ifcFile, setIfcFile] = useState<File | null>(null);
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
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl md:text-4xl font-bold text-gray-800 dark:text-gray-100">
              欢迎, <span className="text-blue-600 dark:text-blue-400">{session.user.name || "用户"}</span>
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-2">
              {session.user.email}
            </p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => router.push("/tasks")}>
              查看任务
            </Button>
            <Button variant="outline" onClick={() => router.push("/ids_use")}>
              文件管理
            </Button>
            <Button variant="outline" onClick={handleSignOut}>
              退出登录
            </Button>
          </div>
        </div>

        {/* Main Form */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8">
          <h2 className="text-2xl font-bold mb-6 text-gray-800 dark:text-gray-100">
            创建 IDS 规范
          </h2>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Text Input */}
            <div className="space-y-2">
              <Label htmlFor="ids-text" className="text-base font-semibold">
                输入 IDS 需求描述 <span className="text-red-500">*</span>
              </Label>
              <Textarea
                id="ids-text"
                placeholder="请输入您的IDS需求，例如：&#10;- 所有IfcWall的防火等级必须为A级&#10;- 门的宽度必须大于900mm&#10;- 楼板的承重必须大于500kg/m²"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                className="min-h-[200px] text-base"
                disabled={isSubmitting}
              />
              <p className="text-sm text-gray-500">
                请用自然语言描述您的IDS规范要求
              </p>
            </div>

            {/* IFC File Upload (Disabled - Phase 3) */}
            <div className="space-y-2">
              <Label htmlFor="ifc-file" className="text-base font-semibold text-gray-400">
                上传 IFC 文件 (第三阶段启用)
              </Label>
              <Input
                id="ifc-file"
                type="file"
                accept=".ifc"
                disabled={true}
                onChange={(e) => setIfcFile(e.target.files?.[0] || null)}
                className="cursor-not-allowed opacity-50"
              />
              <p className="text-sm text-gray-400">
                此功能将在第三阶段开放，用于审核生成的IDS文件
              </p>
            </div>

            {/* Submit Button */}
            <div className="flex justify-end gap-4">
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
                className="min-w-[120px]"
              >
                {isSubmitting ? (
                  <span className="flex items-center gap-2">
                    <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"></path>
                    </svg>
                    提交中...
                  </span>
                ) : (
                  "生成 IDS"
                )}
              </Button>
            </div>
          </form>
        </div>

        {/* Quick Links */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h3 className="font-bold text-lg mb-2">📝 阶段一</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              输入需求文本，生成规范JSON
            </p>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 opacity-50">
            <h3 className="font-bold text-lg mb-2">🔄 阶段二</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              将JSON转换为IDS文件
            </p>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 opacity-50">
            <h3 className="font-bold text-lg mb-2">✅ 阶段三</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              上传IFC文件进行审核
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}