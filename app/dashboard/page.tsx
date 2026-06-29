"use client";

import { useSession } from "@/app/lib/auth-client";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { toast } from "sonner";
import { Loader2, Sparkles, FileText, Lightbulb } from "lucide-react";

export default function Dashboard() {
  const { data: session } = useSession();
  const router = useRouter();

  const [inputText, setInputText] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!inputText.trim()) {
      toast.error("请输入 IDS 需求文本");
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
        toast.success("提交成功，正在生成 IDS 文件");
        setInputText("");
        router.push("/tasks");
      } else {
        const error = await response.json();
        toast.error(`提交失败: ${error.error || "未知错误"}`);
      }
    } catch (error) {
      console.error("Submit error:", error);
      toast.error("提交失败，请检查网络连接");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8 pt-12">
      {/* Welcome Section */}
      <div className="text-center pr-12">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          你好，{session?.user?.name || "用户"}
        </h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">
          用自然语言描述你的 IDS 规范需求，AI 帮你生成标准文件
        </p>
      </div>

      {/* Main Input Card */}
      <Card className="border-0 shadow-lg bg-white dark:bg-gray-900 -mx-4">
        <CardHeader>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <CardTitle className="text-lg">生成 IDS 文件</CardTitle>
              <CardDescription>输入 BIM/IFC 规范需求描述</CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-5">
            <Textarea
              placeholder={"请用自然语言描述您的 IDS 规范要求，例如：\n\n• 所有 IfcWall 的防火等级必须为 A 级\n• 门的宽度必须大于 900mm\n• 楼板的承重必须大于 500kg/m²\n• 所有空间必须包含面积属性"}
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              className="min-h-[200px] text-base leading-relaxed resize-none border-gray-200 dark:border-gray-700 focus-visible:ring-blue-500"
              disabled={isSubmitting}
            />

            <div className="flex items-center justify-between">
              <p className="text-sm text-gray-400">
                支持中英文，自动生成符合 IDS 标准的 XML
              </p>
              <div className="flex gap-3">
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
                  className="min-w-[140px] bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700"
                >
                  {isSubmitting ? (
                    <span className="flex items-center gap-2">
                      <Loader2 className="w-4 h-4 animate-spin" />
                      生成中...
                    </span>
                  ) : (
                    <span className="flex items-center gap-2">
                      <FileText className="w-4 h-4" />
                      生成 IDS 文件
                    </span>
                  )}
                </Button>
              </div>
            </div>
          </form>
        </CardContent>
      </Card>

      {/* Tips Card */}
      <Card className="border border-blue-100 dark:border-blue-900/30 bg-blue-50/50 dark:bg-blue-950/20 max-w-2xl mx-auto">
        <CardContent className="py-4">
          <div className="flex gap-3">
            <Lightbulb className="w-5 h-5 text-blue-500 shrink-0 mt-0.5" />
            <div className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
              <p className="font-medium text-gray-800 dark:text-gray-200">使用提示</p>
              <ul className="space-y-1 list-disc list-inside">
                <li>描述尽量具体，包含实体类型、属性名称和约束条件</li>
                <li>生成后可在「任务列表」中下载 IDS 文件或上传 IFC 文件进行合规检查</li>
                <li>支持批量描述多条规则，系统会自动解析并生成对应的 specification</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
