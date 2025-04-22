from fastapi import FastAPI
import json
from pathlib import Path
import uvicorn

app = FastAPI()

@app.get("/")
def read_root():
    return {
        "service": "LLM Gateway",
        "endpoints": {
            "POST /instructions": "Submit LLM instructions",
            "GET /results/{id}": "Get execution result"
        }
    }
QUEUE_FILE = Path("data/instructions.queue")
RESULT_FILE = Path("data/results.json")

@app.post("/instructions")
def add_instruction(instruction: dict):
    """接收LLM指令并写入队列文件"""
    try:
        with open(QUEUE_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(instruction) + "\n")
        return {"status": "queued", "success": True}
    except Exception as e:
        return {"status": str(e), "success": False}

@app.get("/results/{instruction_id}")
def get_result(instruction_id: str):
    """获取指令执行结果"""
    try:
        with open(RESULT_FILE, "r", encoding="utf-8") as f:
            results = json.load(f)
        return results.get(instruction_id, {"status": "not_found"})
    except:
        return {"status": "error_reading_file"}

def run_api():
    """启动API服务"""
    QUEUE_FILE.parent.mkdir(exist_ok=True)
    QUEUE_FILE.touch(exist_ok=True)
    RESULT_FILE.touch(exist_ok=True)
    
    config = uvicorn.Config(app, host="0.0.0.0", port=8000)
    server = uvicorn.Server(config)
    
    try:
        server.run()
    except KeyboardInterrupt:
        print("\nAPI服务已停止")
    except Exception as e:
        print(f"API服务异常: {str(e)}")

if __name__ == "__main__":
    run_api()
