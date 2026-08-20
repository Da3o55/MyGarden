from datetime import date
class TaskScheduler:
    MONTH_NAMES = {"janvier":1,"février":2,"fevrier":2,"mars":3,"avril":4,"mai":5,"juin":6,"juillet":7,"août":8,"aout":8,"septembre":9,"octobre":10,"novembre":11,"décembre":12,"decembre":12}
    def __init__(self,db,timezone): self.db=db; self.timezone=timezone
    def _active(self, value, month):
        if not value: return False
        raw=str(value).lower().replace(" ","")
        if raw in ("tous","touteannée","touteannee","all"): return True
        return any((token.isdigit() and int(token)==month) or self.MONTH_NAMES.get(token)==month for token in raw.replace(";",",").split(","))
    def today(self):
        month=date.today().month; result=list(self.db.today_tasks()); seen={(x.get("plant_id"),x.get("kind")) for x in result}
        for plant in self.db.list_plants():
            for kind, months in (("floraison",plant.flowering_months),("taille",plant.pruning_months),("engrais",plant.fertilizing_months)):
                if self._active(months, month) and (plant.id,kind) not in seen:
                    result.append({"id":None,"plant_id":plant.id,"kind":kind,"due_date":date.today().isoformat(),"completed":0,"common_name":plant.common_name,"seasonal":True})
        return result
