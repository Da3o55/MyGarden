from aiohttp import web
from .models import PlantCreate

def _json(data, status=200): return web.json_response(data, status=status)

def register_routes(app):
    async def health(request): return _json({"status":"ok","service":"mygarden"})
    async def plants(request): return _json([p.to_dict() for p in app["db"].list_plants()])
    async def add_plant(request):
        try: payload=await request.json(); plant=PlantCreate.from_dict(payload); result=app["db"].add_plant(plant); return _json(result.to_dict(),201)
        except (ValueError, KeyError) as e: return _json({"error":str(e)},400)
    async def plant(request):
        pid=int(request.match_info["id"]); item=app["db"].get_plant(pid)
        return _json(item.to_dict() if item else {"error":"Plante inconnue"}, 200 if item else 404)
    async def delete(request):
        app["db"].delete_plant(int(request.match_info["id"])); return _json({"deleted":True})
    async def tasks(request): return _json(app["scheduler"].today())
    async def complete(request):
        tid=int(request.match_info["id"]); app["db"].complete_task(tid); return _json({"completed":True})
    async def trefle(request):
        q=request.query.get("q","").strip()
        if not q: return _json({"error":"q requis"},400)
        return _json(await app["client"].search(q))
    async def dashboard(request):
        return web.FileResponse(Path(__file__).parent.parent / "www" / "index.html")
    app.router.add_get("/api/health",health); app.router.add_get("/api/plants",plants); app.router.add_post("/api/plants",add_plant)
    app.router.add_get("/api/plants/{id}",plant); app.router.add_delete("/api/plants/{id}",delete)
    app.router.add_get("/api/tasks/today",tasks); app.router.add_post("/api/tasks/{id}/complete",complete); app.router.add_get("/api/trefle/search",trefle)
    app.router.add_get("/",dashboard); app.router.add_static("/static", Path(__file__).parent.parent / "www")
