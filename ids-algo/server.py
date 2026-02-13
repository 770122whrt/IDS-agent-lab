import os
import json
import logging
from contextlib import asynccontextmanager

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

# --- 配置日志 ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ids_server")

# --- 数据库连接 ---
# 必须与 Next.js 使用相同的 MONGODB_URI
MONGO_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/ids_db")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时连接
    app.mongodb_client = MongoClient(MONGO_URI)
    app.db = app.mongodb_client.get_database() # 获取默认库
    logger.info(f"✅ Connected to MongoDB at {MONGO_URI}")
    yield
    # 关闭时断开
    app.mongodb_client.close()
    logger.info("🛑 MongoDB connection closed")

app = FastAPI(lifespan=lifespan)

class AnalysisRequest(BaseModel):
    resourceId: str

# --- 核心后台任务 ---
async def process_file_task(resource_id: str, db):
    """
    1. 读状态 -> 2. 读文件 -> 3. 跑算法 -> 4. 存结果 -> 5. 写状态
    """
    fs = gridfs.GridFS(db, collection="uploads")
    resources_col = db["resources"]
    
    logger.info(f"🚀 Starting task for Resource: {resource_id}")
    
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
        # 假设上传的是文本文件 (txt/md/json)
        text_content = grid_out.read().decode("utf-8")
        logger.info(f"📖 Read {len(text_content)} chars from file.")

        # 3. 🔥 调用 Pipeline (A->E) 🔥
        result_json = await run_ids_pipeline(text_content)

        # 4. 存回结果 (存为新的 GridFS 文件)
        original_name = resource.get("originalname", "unknown")
        result_filename = f"{original_name}_result.json"
        
        result_bytes = json.dumps(result_json, ensure_ascii=False, indent=2).encode("utf-8")
        result_file_id = fs.put(result_bytes, filename=result_filename, contentType="application/json")

        # 5. 更新状态为 Completed
        resources_col.update_one(
            {"_id": ObjectId(resource_id)},
            {"$set": {
                "status": "completed",
                "resultFileId": result_file_id,
                "errorMessage": None
            }}
        )
        logger.info(f"✅ Task {resource_id} completed. Result ID: {result_file_id}")

    except Exception as e:
        logger.error(f"❌ Task {resource_id} failed: {e}")
        import traceback
        traceback.print_exc()
        # 记录失败状态
        resources_col.update_one(
            {"_id": ObjectId(resource_id)},
            {"$set": {"status": "failed", "errorMessage": str(e)}}
        )

# --- API 接口 ---
@app.post("/analyze")
async def start_analysis(req: AnalysisRequest, background_tasks: BackgroundTasks):
    """
    Next.js 调用的入口。
    不等待分析完成，直接返回 "OK"，后台慢慢跑。
    """
    logger.info(f"📥 Received analysis request for {req.resourceId}")
    background_tasks.add_task(process_file_task, req.resourceId, app.db)
    return {"message": "Analysis started", "id": req.resourceId}

@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    # 启动服务，端口 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)