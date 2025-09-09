#!/usr/bin/env python3
"""
Simple runner script for RankX Product Research System
"""

import argparse
import sys
import os
from pathlib import Path

def run_fastapi():
    """Run the FastAPI application"""
    try:
        import uvicorn
        from main import app
        print("🚀 Starting FastAPI server...")
        print("📍 Open http://localhost:8000 in your browser")
        uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
    except ImportError:
        print("❌ Error: uvicorn not installed. Run: pip install uvicorn")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting FastAPI: {e}")
        sys.exit(1)

def run_streamlit():
    """Run the Streamlit application"""
    try:
        import subprocess
        print("🚀 Starting Streamlit app...")
        subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_app.py"])
    except Exception as e:
        print(f"❌ Error starting Streamlit: {e}")
        sys.exit(1)

def check_environment():
    """Check if environment is properly configured"""
    print("🔍 Checking environment...")
    
    # Check if .env file exists
    if not Path(".env").exists():
        print("⚠️  .env file not found. Copy .env.example to .env and add your API keys.")
        return False
    
    # Check required API keys
    required_keys = ["OPENAI_API_KEY", "TAVILY_API_KEY", "SCRAPEGRAPH_API_KEY"]
    missing_keys = []
    
    for key in required_keys:
        if not os.getenv(key):
            missing_keys.append(key)
    
    if missing_keys:
        print(f"⚠️  Missing required API keys: {', '.join(missing_keys)}")
        print("   Please add them to your .env file.")
        return False
    
    print("✅ Environment configuration looks good!")
    return True

def install_dependencies():
    """Install required dependencies"""
    try:
        import subprocess
        print("📦 Installing dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="RankX Product Research System Runner")
    parser.add_argument(
        "interface",
        choices=["fastapi", "streamlit", "api", "web"],
        help="Choose interface to run (fastapi/api for REST API, streamlit/web for web interface)"
    )
    parser.add_argument(
        "--check-env",
        action="store_true",
        help="Check environment configuration"
    )
    parser.add_argument(
        "--install",
        action="store_true",
        help="Install dependencies"
    )
    parser.add_argument(
        "--no-env-check",
        action="store_true",
        help="Skip environment check"
    )
    
    args = parser.parse_args()
    
    print("🤖 RankX Product Research System")
    print("=" * 50)
    
    # Install dependencies if requested
    if args.install:
        install_dependencies()
    
    # Check environment unless skipped
    if not args.no_env_check:
        if not check_environment():
            print("\n💡 Fix the environment issues above and try again.")
            sys.exit(1)
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("⚠️  python-dotenv not installed. Install it for .env file support.")
    
    # Run the selected interface
    if args.interface in ["fastapi", "api"]:
        run_fastapi()
    elif args.interface in ["streamlit", "web"]:
        run_streamlit()

if __name__ == "__main__":
    main()