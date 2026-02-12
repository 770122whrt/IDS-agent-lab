# ids-algo/server.py
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
import gridfs
from bson.objectid import ObjectId
import os
import json
from pipeline import run_ids_pipeline # 引入上面的流水线

app = FastAPI()

# 数据库连接 (读取环境变量或硬编码测试)
MONGO_URI = os.getenv("MONGODB_URI", "mongodb+srv://haoyuwang:770122@cluster0.maypzsy.mongodb.net/IDS-agent?appName=Cluster0") # 务必与 Next.js 使用同一个库
client = MongoClient(MONGO_URI)
db = client.get_database() # 获取默认数据库
fs = gridfs.GridFS(db, collection="uploads") # 对应 Next.js 的 uploads.files
resources_col = db["resources"] # 对应 Next.js 的 Resource 表

class AnalysisRequest(BaseModel):
    resourceId: str

def process_file_task(resource_id: str):
    """后台任务：处理文件"""
    try:
        # 1. 更新状态为 processing
        resources_col.update_one(
            {"_id": ObjectId(resource_id)},
            {"$set": {"status": "processing"}}
        )

        # 2. 获取文件信息
        resource = resources_col.find_one({"_id": ObjectId(resource_id)})
        file_id = resource["fileId"]

        # 3. 从 GridFS 读取原始文件
        grid_out = fs.get(file_id)
        content = grid_out.read().decode("utf-8") # 假设上传的是文本/Markdown

        # 4. 运行算法流水线
        result_json = run_ids_pipeline(content)
        
        # 5. 将结果存回 GridFS
        # 结果文件名：原始文件名_result.json
        result_filename = f"{resource['originalname']}_result.json"
        result_bytes = json.dumps(result_json, ensure_ascii=False, indent=2).encode("utf-8")
        
        result_file_id = fs.put(result_bytes, filename=result_filename, contentType="application/json")

        # 6. 更新状态为 completed 并关联结果文件
        resources_col.update_one(
            {"_id": ObjectId(resource_id)},
            {"$set": {
                "status": "completed",
                "resultFileId": result_file_id
            }}
        )
        print(f"Task {resource_id} completed successfully.")

    except Exception as e:
        print(f"Task {resource_id} failed: {e}")
        resources_col.update_one(
            {"_id": ObjectId(resource_id)},
            {"$set": {"status": "failed", "errorMessage": str(e)}}
        )

@app.post("/analyze")
async def start_analysis(req: AnalysisRequest, background_tasks: BackgroundTasks):
    """接收分析请求，立即返回，后台处理"""
    # 简单的校验
    resource = resources_col.find_one({"_id": ObjectId(req.resourceId)})
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    # 添加到后台任务队列
    background_tasks.add_task(process_file_task, req.resourceId)
    
    return {"message": "Analysis started", "resourceId": req.resourceId}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)