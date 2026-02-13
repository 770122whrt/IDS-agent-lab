from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
import gridfs
from bson.objectid import ObjectId
import os
import json
import logging
from typing import Optional

# 引入刚才写好的 pipeline
from pipeline import run_ids_pipeline

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ids_server")

app = FastAPI()

# 数据库连接
MONGO_URI = os.getenv("MONGODB_URI")
if not MONGO_URI:
    logger.warning("MONGODB_URI not set, using default localhost")
    MONGO_URI = "mongodb://localhost:27017/ids_db" # 默认值，根据实际情况修改

client = MongoClient(MONGO_URI)
# 注意：你需要确认你的 Next.js 连接的是哪个库名，通常在 URI 里或者默认是 test
# 这里假设库名是 'sample_mflix' (根据你之前的 .env) 或者你项目特定的库
db_name = MONGO_URI.split("/")[-1].split("?")[0] or "test"
db = client[db_name] 

fs = gridfs.GridFS(db, collection="uploads")
resources_col = db["resources"] # 对应 Next.js 中的 Resource Model

class AnalysisRequest(BaseModel):
    resourceId: str

async def process_file_task(resource_id: str):
    """后台异步任务"""
    logger.info(f"Starting task for Resource ID: {resource_id}")
    try:
        # 1. 更新状态 -> Processing
        resources_col.update_one(
            {"_id": ObjectId(resource_id)},
            {"$set": {"status": "processing"}}
        )

        # 2. 从数据库获取文件信息
        resource = resources_col.find_one({"_id": ObjectId(resource_id)})
        if not resource:
            raise Exception("Resource not found in DB")
        
        file_id = resource.get("fileId") # 这是一个 ObjectId

        # 3. 读取 GridFS 文件内容
        if not fs.exists(file_id):
             raise Exception(f"File {file_id} not found in GridFS")
             
        grid_out = fs.get(file_id)
        # 假设文件是文本格式 (txt, md, json等)，进行 UTF-8 解码
        text_content = grid_out.read().decode("utf-8")

        # 4. 🔥 调用核心 Pipeline 🔥
        result_json = await run_ids_pipeline(text_content)

        # 5. 将结果存回 GridFS
        # 结果文件名：原文件名_result.json
        original_name = resource.get("originalname", "unknown")
        result_filename = f"{original_name}_ids_result.json"
        
        # 序列化 JSON
        result_bytes = json.dumps(result_json, ensure_ascii=False, indent=2).encode("utf-8")
        
        # 存入 GridFS
        result_file_id = fs.put(result_bytes, filename=result_filename, contentType="application/json")

        # 6. 更新状态 -> Completed
        resources_col.update_one(
            {"_id": ObjectId(resource_id)},
            {"$set": {
                "status": "completed",
                "resultFileId": result_file_id,
                "errorMessage": None # 清除之前的错误
            }}
        )
        logger.info(f"Task {resource_id} completed. Result saved as {result_filename}")

    except Exception as e:
        logger.error(f"Task {resource_id} failed: {e}")
        # 记录错误信息到数据库
        resources_col.update_one(
            {"_id": ObjectId(resource_id)},
            {"$set": {
                "status": "failed", 
                "errorMessage": str(e)
            }}
        )

@app.post("/analyze")
async def start_analysis(req: AnalysisRequest, background_tasks: BackgroundTasks):
    """前端调用的触发接口"""
    # 简单的 ID 校验
    try:
        obj_id = ObjectId(req.resourceId)
    except:
        raise HTTPException(status_code=400, detail="Invalid Resource ID format")

    resource = resources_col.find_one({"_id": obj_id})
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    # 将任务丢给后台运行，立即返回响应给前端
    background_tasks.add_task(process_file_task, req.resourceId)
    
    return {"message": "Analysis started", "resourceId": req.resourceId}

if __name__ == "__main__":
    import uvicorn
    # 启动服务，端口 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)