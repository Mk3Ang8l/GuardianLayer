try:
    import uvicorn
except ImportError:
    print("to run the server, install the missing dependencies:")
    print("   pip install GuardianLayer[server]")
    exit(1)

uvicorn.run("GuardianLayer.server:app", host="0.0.0.0", port=8000, reload=False)
