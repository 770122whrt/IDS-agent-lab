import asyncio
import json
import os
import logging
from pathlib import Path

# 引入我们刚才写好的 pipeline
from pipeline import run_ids_pipeline

# 配置日志，让我们能看到 pipeline 内部的打印信息 (比如 Merged count)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("LocalTest")

async def main():
    # 1. 准备测试输入
    # 尝试从 temp/input.json 读取，如果失败则用默认文本
    input_file = Path("temp/input.json")
    test_inputs = []

    if input_file.exists():
        try:
            with open(input_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    test_inputs = data
                else:
                    test_inputs = [data]
            logger.info(f"Loaded {len(test_inputs)} entries from input.json")
        except Exception as e:
            logger.warning(f"Failed to read input.json: {e}")
    
    # 如果没有文件，使用默认测试用例
    if not test_inputs:
        logger.info("Using default test case.")
        test_inputs = [
            {
                "id": "test_001", 
                "text": "All structural columns must be made of Concrete with a compressive strength greater than 30MPa."
            }
        ]

    # 2. 循环测试
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    for entry in test_inputs:
        entry_id = str(entry.get("id", "unknown"))
        text = entry.get("text", "")
        
        if not text:
            continue

        print(f"\n{'='*50}")
        print(f"🧪 Testing Entry ID: {entry_id}")
        print(f"📝 Text: {text[:60]}...")
        print(f"{'='*50}")

        try:
            # 🔥 调用整个 Pipeline
            # 这会触发 A->B->C->D -> (E的Merge逻辑) -> E的Builder
            final_result = await run_ids_pipeline(text)

            # 3. 保存结果
            output_path = output_dir / f"pipeline_result_{entry_id}.json"
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(final_result, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Success! Result saved to: {output_path}")
            
            # 简单的验证：检查结果里有没有 specifications
            specs = final_result.get("specifications", [])
            print(f"📊 Generated {len(specs)} specifications.")
            
            # 🔍 验证 C+D 的合成效果
            # 如果成功，specifications 里应该有 requirements
            if specs:
                reqs = specs[0].get("requirements", [])
                print(f"   First spec has {len(reqs)} requirements.")

        except Exception as e:
            print(f"❌ Failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    # 确保 API Key 存在
    if not os.getenv("OPENROUTER_API_KEY"):
        print("⚠️  Warning: OPENROUTER_API_KEY not found in environment variables.")
        print("   Run 'export OPENROUTER_API_KEY=...' before running this script.")
    
    asyncio.run(main())