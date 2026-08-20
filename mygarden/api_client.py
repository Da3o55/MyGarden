import aiohttp
class TrefleClient:
    BASE="https://trefle.io/api/v1"
    def __init__(self,token): self.token=token
    async def search(self,q):
        if not self.token: return {"error":"Jeton Trefle non configuré","results":[]}
        try:
            async with aiohttp.ClientSession() as s:
                async with s.get(self.BASE+"/plants/search",params={"q":q,"token":self.token},timeout=15) as r:
                    if r.status!=200: return {"error":f"Trefle HTTP {r.status}","results":[]}
                    return await r.json()
        except aiohttp.ClientError as e: return {"error":str(e),"results":[]}
