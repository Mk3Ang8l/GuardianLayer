try:
    import uvicorn
except ImportError:
    print("❌ Pour lancer le serveur installe les dépendances manquantes :")
    print("   pip install GuardianLayer[server]")
    exit(1)

uvicorn.run("GuardianLayer.server:app", host="0.0.0.0", port=8000, reload=False)
