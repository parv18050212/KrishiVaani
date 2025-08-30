import uvicorn
from ocr import app

if __name__ == "__main__":
    uvicorn.run(
        "ocr:app",
        host="0.0.0.0",
        port=8003,
        reload=True,
        log_level="info"
    )
