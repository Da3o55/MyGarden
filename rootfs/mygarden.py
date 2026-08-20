#!/usr/bin/env python3
"""Point d'entrée du service MyGarden pour l'addon Home Assistant."""
import asyncio, json, os
from pathlib import Path
from mygarden.api_client import TrefleClient
from mygarden.database import GardenDB
from mygarden.scheduler import TaskScheduler
from mygarden.utils import load_options
from aiohttp import web

async def main():
    options=load_options()
    db=GardenDB(os.getenv("MYGARDEN_DB", "/data/mygarden.db"))
    client=TrefleClient(options.get("trefle_token", ""))
    scheduler=TaskScheduler(db, options.get("timezone", "Europe/Paris"))
    app=web.Application()
    app["db"]=db; app["client"]=client; app["scheduler"]=scheduler
    from mygarden import register_routes
    register_routes(app)
    runner=web.AppRunner(app); await runner.setup()
    site=web.TCPSite(runner,"0.0.0.0",8099); await site.start()
    print("MyGarden écoute sur le port 8099")
    await asyncio.Event().wait()
if __name__ == "__main__": asyncio.run(main())
