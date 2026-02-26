"""
IDS Agent Python Backend Server

纯数据库存储架构：
- IDS 文件存储到 GridFS
- IFC 文件存储到 GridFS
- 审查报告存储为 JSON
- 使用临时文件对接 ifctester，审查完成后立即删除

作者: IDS-Agent
版本: 2.0.0
"""

import os
import json
import logging
import tempfile
from contextlib import asynccontextmanager
from pathlib import Path
from datetime import datetime
from typing import Any

from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
import gridfs
from bson.objectid import ObjectId

from dotenv import load_dotenv
# 明确指定你要读取的环境变量文件名
load_dotenv(".env-pipeline")

# 引入你验证过的 pipeline
from pipeline import run_ids_pipeline

# 引入 IDS 转换器
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "ids_converter"))
from converter import convert_json_to_ids_xml, XSDValidationError, IDSConversionError

# 引入 IFC 检查器
sys.path.insert(0, str(Path(__file__).parent.parent / "ifc_checker"))
from checker_service import check_ifc_against_ids

# --- 配置日志 ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ids_server")


# =============================================================================
# BSON 序列化清洗函数
# =============================================================================

def sanitize_for_bson(obj: Any) -> Any:
    """
    递归清洗数据，确保所有值都能被 BSON 序列化

    ifctester 返回的报告数据中可能包含自定义 Python 对象（如 Restriction 类实例），
    这些对象无法直接存入 MongoDB。此函数将：
    1. 将字典递归清洗
    2. 将列表递归清洗
    3. 将无法序列化的对象转换为字符串表示
    """
    if obj is None:
        return None

    if isinstance(obj, (str, int, float, bool)):
        return obj

    if isinstance(obj, dict):
        return {key: sanitize_for_bson(value) for key, value in obj.items()}

    if isinstance(obj, (list, tuple)):
        return [sanitize_for_bson(item) for item in obj]

    # 对于 datetime 等基本类型，保持原样
    if isinstance(obj, datetime):
        return obj

    # 对于其他类型（自定义对象等），尝试转换为字符串
    try:
        # 尝试 JSON 序列化测试
        json.dumps(obj)
        return obj
    except (TypeError, ValueError):
        # 无法序列化，转换为字符串
        logger.warning(f"Converting non-serializable object to string: {type(obj)}")
        return str(obj)


def deep_json_sanitize(obj: Any) -> Any:
    """
    使用 JSON 序列化/反序列化进行深度清洗

    这是一种"黑科技"方法：通过 JSON 的 default=str 处理所有无法直接序列化的对象，
    然后再解析回来，确保结果只包含基本 JSON 类型。
    """
    try:
        json_str = json.dumps(obj, default=str, ensure_ascii=False)
        return json.loads(json_str)
    except Exception as e:
        logger.error(f"Failed to sanitize object: {e}")
        # 降级处理：返回字符串表示
        return str(obj)

# --- XSD Schema 路径 ---
XSD_PATH = Path(__file__).parent.parent / "ids_converter" / "ids.xsd"

# --- 数据库连接 ---
# 必须与 Next.js 使用相同的 MONGODB_URI
MONGO_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/ids_db")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时连接
    app.mongodb_client = MongoClient(MONGO_URI)
    app.db = app.mongodb_client.get_database()
    logger.info(f"✅ Connected to MongoDB at {MONGO_URI}")
    yield
    # 关闭时断开
    app.mongodb_client.close()
    logger.info("🛑 MongoDB connection closed")


app = FastAPI(lifespan=lifespan)


# =============================================================================
# 请求模型
# =============================================================================

class AnalysisRequest(BaseModel):
    resourceId: str

class TextAnalysisRequest(BaseModel):
    resourceId: str
    text: str

class IFCCheckRequest(BaseModel):
    taskId: str
    idsFileId: str  # GridFS 中的 IDS 文件 ID
    ifcFileId: str  # GridFS 中的 IFC 文件 ID


# =============================================================================
# 核心后台任务
# =============================================================================

async def process_file_task(resource_id: str, db):
    """
    处理文件上传分析的后台任务（保留原有逻辑）
    """
    fs = gridfs.GridFS(db, collection="uploads")
    resources_col = db["resources"]

    logger.info(f"🚀 Starting file task for Resource: {resource_id}")

    try:
        # 1. 更新状态为 Processing
        resources_col.update_one(
            {"_id": ObjectId(resource_id)},
            {"$set": {"status": "processing"}}
        )

        # 2. 获取元数据 & 读取文件
        resource = resources_col.find_one({"_id": ObjectId(resource_id)})
        if not resource:
            raise Exception("Resource doc not found")

        file_id = resource.get("fileId")
        if not fs.exists(file_id):
            raise Exception("GridFS file not found")

        grid_out = fs.get(file_id)
        text_content = grid_out.read().decode("utf-8")
        logger.info(f"📖 Read {len(text_content)} chars from file.")

        # 3. 调用 Pipeline
        result_json = await run_ids_pipeline(text_content)

        # 4. 存储结果到 GridFS
        original_name = resource.get("originalname", "unknown")
        result_filename = f"{original_name}_result.json"
        result_bytes = json.dumps(result_json, ensure_ascii=False, indent=2).encode("utf-8")
        result_file_id = fs.put(result_bytes, filename=result_filename, contentType="application/json")

        # 5. 更新状态
        resources_col.update_one(
            {"_id": ObjectId(resource_id)},
            {"$set": {
                "status": "completed",
                "resultFileId": result_file_id,
                "errorMessage": None
            }}
        )
        logger.info(f"✅ File task {resource_id} completed. Result ID: {result_file_id}")

    except Exception as e:
        logger.error(f"❌ File task {resource_id} failed: {e}")
        import traceback
        traceback.print_exc()
        resources_col.update_one(
            {"_id": ObjectId(resource_id)},
            {"$set": {"status": "failed", "errorMessage": str(e)}}
        )


async def process_text_task(resource_id: str, text_content: str, db):
    """
    处理文本输入的后台任务
    IDS 文件存储到 GridFS（纯数据库存储架构）
    """
    fs = gridfs.GridFS(db, collection="uploads")
    resources_col = db["resources"]

    logger.info(f"🚀 Starting text processing task for Resource: {resource_id}")

    try:
        # 1. 更新状态为 Processing
        resources_col.update_one(
            {"_id": ObjectId(resource_id)},
            {"$set": {"status": "processing"}}
        )

        # 2. 调用 Pipeline
        logger.info(f"📖 Processing {len(text_content)} chars of text.")
        result_json = await run_ids_pipeline(text_content)

        # 3. 转换 JSON 为 IDS XML
        logger.info(f"🔄 Converting JSON to IDS XML...")
        try:
            ids_xml_content = convert_json_to_ids_xml(
                result_json,
                xsd_path=str(XSD_PATH),
                title=None,
                copyright="Generated by IDS-Agent",
                version="1.0",
            )
            logger.info(f"✅ IDS XML conversion successful, XSD validation passed")
        except XSDValidationError as xsd_error:
            error_msg = f"XSD Validation Failed: {str(xsd_error)}"
            logger.error(f"❌ {error_msg}")
            resources_col.update_one(
                {"_id": ObjectId(resource_id)},
                {"$set": {
                    "status": "failed",
                    "resultJson": result_json,
                    "errorMessage": error_msg
                }}
            )
            return
        except IDSConversionError as conv_error:
            error_msg = f"IDS Conversion Error: {str(conv_error)}"
            logger.error(f"❌ {error_msg}")
            resources_col.update_one(
                {"_id": ObjectId(resource_id)},
                {"$set": {
                    "status": "failed",
                    "resultJson": result_json,
                    "errorMessage": error_msg
                }}
            )
            return

        # 4. 存储 IDS 文件到 GridFS
        ids_filename = f"{resource_id}.ids"
        ids_bytes = ids_xml_content.encode('utf-8')
        ids_file_id = fs.put(
            ids_bytes,
            filename=ids_filename,
            contentType="application/xml"
        )
        logger.info(f"💾 IDS file saved to GridFS with ID: {ids_file_id}")

        # 5. 更新状态为 Completed
        resources_col.update_one(
            {"_id": ObjectId(resource_id)},
            {"$set": {
                "status": "completed",
                "resultJson": result_json,
                "idsFileId": ids_file_id,
                "idsFileName": ids_filename,
                "errorMessage": None
            }}
        )
        logger.info(f"✅ Text task {resource_id} completed successfully")

    except Exception as e:
        logger.error(f"❌ Text task {resource_id} failed: {e}")
        import traceback
        traceback.print_exc()
        resources_col.update_one(
            {"_id": ObjectId(resource_id)},
            {"$set": {"status": "failed", "errorMessage": str(e)}}
        )


async def process_ifc_check_task(task_id: str, ids_file_id: str, ifc_file_id: str, db):
    """
    处理 IFC 审查的后台任务
    使用临时文件对接 ifctester，审查完成后立即删除临时文件
    """
    fs = gridfs.GridFS(db, collection="uploads")
    resources_col = db["resources"]

    logger.info(f"🔍 Starting IFC check task: {task_id}")

    ids_temp_file = None
    ifc_temp_file = None

    try:
        # 1. 更新状态为 checking
        resources_col.update_one(
            {"_id": ObjectId(task_id)},
            {"$set": {"status": "checking"}}
        )

        # 2. 从 GridFS 读取 IDS 文件，写入临时文件
        if not fs.exists(ObjectId(ids_file_id)):
            raise Exception(f"IDS file not found in GridFS: {ids_file_id}")

        ids_grid_out = fs.get(ObjectId(ids_file_id))
        ids_content = ids_grid_out.read()

        # 创建临时 IDS 文件
        ids_temp_file = tempfile.NamedTemporaryFile(
            mode='wb',
            suffix='.ids',
            delete=False
        )
        ids_temp_file.write(ids_content)
        ids_temp_file.close()
        ids_temp_path = ids_temp_file.name
        logger.info(f"📁 IDS temp file created: {ids_temp_path}")

        # 3. 从 GridFS 读取 IFC 文件，写入临时文件
        if not fs.exists(ObjectId(ifc_file_id)):
            raise Exception(f"IFC file not found in GridFS: {ifc_file_id}")

        ifc_grid_out = fs.get(ObjectId(ifc_file_id))
        ifc_content = ifc_grid_out.read()

        # 创建临时 IFC 文件
        ifc_temp_file = tempfile.NamedTemporaryFile(
            mode='wb',
            suffix='.ifc',
            delete=False
        )
        ifc_temp_file.write(ifc_content)
        ifc_temp_file.close()
        ifc_temp_path = ifc_temp_file.name
        logger.info(f"📁 IFC temp file created: {ifc_temp_path}")

        # 4. 调用审查函数
        logger.info(f"🔍 Running IDS validation against IFC model...")
        result = check_ifc_against_ids(
            ids_file_path=ids_temp_path,
            ifc_file_path=ifc_temp_path,
            output_dir=None  # 不生成物理报告文件，只返回数据
        )

        # 5. 处理结果
        if result["success"]:
            logger.info(f"✅ IFC check completed: {result['message']}")
            logger.info(f"   Summary: {result['summary']}")

            # 报告数据已在 checker_service 中清洗，直接使用
            report_data = result.get("report_data")
            if report_data:
                logger.info(f"📊 Report data ready, specs count: {len(report_data.get('specifications', []))}")

            # 更新任务状态为 checked
            resources_col.update_one(
                {"_id": ObjectId(task_id)},
                {"$set": {
                    "status": "checked",
                    "reportData": report_data,
                    "reportSummary": result.get("summary"),
                    "checkedAt": datetime.now(),
                    "errorMessage": None
                }}
            )
        else:
            logger.error(f"❌ IFC check failed: {result['message']}")

            # 更新任务状态为 check_failed
            resources_col.update_one(
                {"_id": ObjectId(task_id)},
                {"$set": {
                    "status": "check_failed",
                    "errorMessage": result["message"]
                }}
            )

    except Exception as e:
        logger.error(f"❌ IFC check task {task_id} failed: {e}")
        import traceback
        traceback.print_exc()

        resources_col.update_one(
            {"_id": ObjectId(task_id)},
            {"$set": {
                "status": "check_failed",
                "errorMessage": str(e)
            }}
        )

    finally:
        # 6. 清理临时文件（重要！）
        if ids_temp_file and os.path.exists(ids_temp_file.name):
            try:
                os.unlink(ids_temp_file.name)
                logger.info(f"🧹 Cleaned up IDS temp file: {ids_temp_file.name}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to clean up IDS temp file: {e}")

        if ifc_temp_file and os.path.exists(ifc_temp_file.name):
            try:
                os.unlink(ifc_temp_file.name)
                logger.info(f"🧹 Cleaned up IFC temp file: {ifc_temp_file.name}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to clean up IFC temp file: {e}")


# 需要导入 datetime
from datetime import datetime


# =============================================================================
# API 接口
# =============================================================================

@app.post("/analyze")
async def start_analysis(req: AnalysisRequest, background_tasks: BackgroundTasks):
    """
    文件分析入口（保留原有功能）
    """
    logger.info(f"📥 Received analysis request for {req.resourceId}")
    background_tasks.add_task(process_file_task, req.resourceId, app.db)
    return {"message": "Analysis started", "id": req.resourceId}


@app.post("/analyze-text")
async def start_text_analysis(req: TextAnalysisRequest, background_tasks: BackgroundTasks):
    """
    文本分析入口
    IDS 文件存储到 GridFS
    """
    logger.info(f"📥 Received text analysis request for {req.resourceId}")
    background_tasks.add_task(process_text_task, req.resourceId, req.text, app.db)
    return {"message": "Text analysis started", "id": req.resourceId}


@app.post("/check-ifc")
async def check_ifc(req: IFCCheckRequest, background_tasks: BackgroundTasks):
    """
    IFC 审查入口
    使用后台任务执行审查，支持大文件和长时间处理
    """
    logger.info(f"📥 Received IFC check request for task: {req.taskId}")
    logger.info(f"   IDS File ID: {req.idsFileId}")
    logger.info(f"   IFC File ID: {req.ifcFileId}")

    # 验证任务存在
    resources_col = app.db["resources"]
    task = resources_col.find_one({"_id": ObjectId(req.taskId)})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # 添加后台任务
    background_tasks.add_task(
        process_ifc_check_task,
        req.taskId,
        req.idsFileId,
        req.ifcFileId,
        app.db
    )

    return {"message": "IFC check started", "taskId": req.taskId}


@app.get("/health")
def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)