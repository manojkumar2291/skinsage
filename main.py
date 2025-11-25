# main.py (Root directory)
import uvicorn
from app.main import app

if __name__ == "__main__":
    # You can customize startup logging here based on app.core.config.settings
    print("=" * 60)
    print("🩺 Skin/Hair Issue Analyzer - Starting Server (Refactored Structure)")
    print("=" * 60)
    
    uvicorn.run(
        "main:app", 
        host="127.0.0.1", 
        port=8000, 
        reload=True,
        log_level="info"
    )