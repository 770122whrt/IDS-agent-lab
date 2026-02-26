import { NextRequest, NextResponse } from "next/server";
import { dbConnect } from "../../../../../backend/mongodb";
import { Resource } from "../../../../../backend/resource";
import { writeFile, mkdir, access } from "fs/promises";
import { constants } from "fs";
import path from "path";

// Next.js 15 要求 params 必须是一个 Promise 类型
type ContextType = {
  params: Promise<{ id: string }>;
};

// 存储目录配置
const UPLOADS_DIR = path.join(process.cwd(), "uploads");
const IFC_FILES_DIR = path.join(UPLOADS_DIR, "ifc_files");
const REPORTS_DIR = path.join(UPLOADS_DIR, "reports");

// POST: 上传 IFC 文件并执行审查
export async function POST(
  request: NextRequest,
  context: ContextType
) {
  try {
    await dbConnect();

    const { id } = await context.params;
    const taskId = id;

    if (!taskId) {
      return NextResponse.json(
        { error: "任务ID缺失" },
        { status: 400 }
      );
    }

    // 查找任务
    const task = await Resource.findById(taskId);

    if (!task) {
      return NextResponse.json(
        { error: "任务不存在" },
        { status: 404 }
      );
    }

    // 检查任务状态
    if (task.status !== "completed") {
      return NextResponse.json(
        { error: "任务尚未完成 IDS 生成，无法进行审查" },
        { status: 400 }
      );
    }

    // 检查 IDS 文件是否存在
    if (!task.idsFilePath) {
      return NextResponse.json(
        { error: "IDS 文件不存在，请先生成 IDS 文件" },
        { status: 400 }
      );
    }

    // 验证 IDS 文件物理存在
    try {
      await access(task.idsFilePath, constants.F_OK);
    } catch {
      return NextResponse.json(
        { error: "IDS 文件在服务器上不存在" },
        { status: 400 }
      );
    }

    // 解析 FormData
    const formData = await request.formData();
    const ifcFile = formData.get("ifc") as File | null;

    if (!ifcFile) {
      return NextResponse.json(
        { error: "未找到 IFC 文件" },
        { status: 400 }
      );
    }

    // 验证文件类型
    if (!ifcFile.name.toLowerCase().endsWith(".ifc")) {
      return NextResponse.json(
        { error: "只支持 .ifc 格式的文件" },
        { status: 400 }
      );
    }

    // 确保存储目录存在
    await mkdir(IFC_FILES_DIR, { recursive: true });
    await mkdir(REPORTS_DIR, { recursive: true });

    // 保存 IFC 文件
    const ifcFileName = `${taskId}_${Date.now()}.ifc`;
    const ifcFilePath = path.join(IFC_FILES_DIR, ifcFileName);
    const ifcBuffer = Buffer.from(await ifcFile.arrayBuffer());
    await writeFile(ifcFilePath, ifcBuffer);

    console.log(`[IFC Check] IFC 文件已保存: ${ifcFilePath}`);
    console.log(`[IFC Check] IDS 文件路径: ${task.idsFilePath}`);

    // 创建报告输出目录
    const reportDir = path.join(REPORTS_DIR, taskId);
    await mkdir(reportDir, { recursive: true });

    // 调用 Python 后端执行审查
    const PYTHON_API_URL = process.env.PYTHON_API_URL || "http://localhost:8000";

    const checkResponse = await fetch(`${PYTHON_API_URL}/check-ifc`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        taskId: taskId,
        idsFilePath: task.idsFilePath,
        ifcFilePath: ifcFilePath,
        reportDir: reportDir,
      }),
    });

    if (!checkResponse.ok) {
      const errorText = await checkResponse.text();
      console.error("[IFC Check] Python 服务错误:", errorText);

      // 更新任务状态为失败
      await Resource.findByIdAndUpdate(taskId, {
        $set: {
          status: "check_failed",
          errorMessage: "IFC 审查失败: " + errorText,
        }
      });

      return NextResponse.json(
        { error: "IFC 审查失败", details: errorText },
        { status: 500 }
      );
    }

    const checkResult = await checkResponse.json();
    console.log("[IFC Check] 审查结果:", checkResult);

    // 更新任务记录
    const updateData: Record<string, unknown> = {
      status: "checked",
      ifcFilePath: ifcFilePath,
      reportDir: reportDir,
      checkedAt: new Date(),
      errorMessage: null,
    };

    // 保存报告摘要
    if (checkResult.summary) {
      updateData.reportSummary = checkResult.summary;
    }

    // 保存报告数据路径
    if (checkResult.json_report_path) {
      updateData.reportJsonPath = checkResult.json_report_path;
    }
    if (checkResult.html_report_path) {
      updateData.reportHtmlPath = checkResult.html_report_path;
    }

    await Resource.findByIdAndUpdate(taskId, { $set: updateData });

    return NextResponse.json({
      success: true,
      message: checkResult.message || "IFC 审查完成",
      summary: checkResult.summary,
      reportData: checkResult.report_data,
    });

  } catch (error) {
    console.error("IFC 审查错误:", error);
    return NextResponse.json(
      { error: "服务器内部错误", details: error instanceof Error ? error.message : String(error) },
      { status: 500 }
    );
  }
}