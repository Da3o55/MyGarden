import sqlite3
from datetime import datetime, date
from .models import Plant, PlantCreate
class GardenDB:
    def __init__(self,path):
        self.path=path; self.conn=sqlite3.connect(path,check_same_thread=False); self.conn.row_factory=sqlite3.Row; self.init()
    def init(self):
        self.conn.executescript("""CREATE TABLE IF NOT EXISTS plants (id INTEGER PRIMARY KEY AUTOINCREMENT, common_name TEXT NOT NULL, scientific_name TEXT, family TEXT, variety TEXT, location TEXT, sun_exposure TEXT, watering_frequency_days INTEGER DEFAULT 7, flowering_months TEXT, pruning_months TEXT, fertilizing_months TEXT, notes TEXT, trefle_id INTEGER, created_at TEXT NOT NULL, updated_at TEXT NOT NULL); CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, plant_id INTEGER NOT NULL, kind TEXT NOT NULL, due_date TEXT NOT NULL, completed INTEGER DEFAULT 0, FOREIGN KEY(plant_id) REFERENCES plants(id) ON DELETE CASCADE);"""); self.conn.commit()
    def _plant(self,r): return Plant(**dict(r))
    def list_plants(self): return [self._plant(r) for r in self.conn.execute("SELECT * FROM plants ORDER BY common_name")]
    def get_plant(self,pid):
        r=self.conn.execute("SELECT * FROM plants WHERE id=?",(pid,)).fetchone(); return self._plant(r) if r else None
    def add_plant(self,p):
        now=datetime.utcnow().isoformat(); fields=[p.common_name,p.scientific_name,p.family,p.variety,p.location,p.sun_exposure,p.watering_frequency_days,p.flowering_months,p.pruning_months,p.fertilizing_months,p.notes,p.trefle_id,now,now]
        cur=self.conn.execute("INSERT INTO plants (common_name,scientific_name,family,variety,location,sun_exposure,watering_frequency_days,flowering_months,pruning_months,fertilizing_months,notes,trefle_id,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",fields); self.conn.commit(); return self.get_plant(cur.lastrowid)
    def delete_plant(self,pid): self.conn.execute("DELETE FROM plants WHERE id=?",(pid,)); self.conn.commit()
    def today_tasks(self):
        rows=self.conn.execute("SELECT t.*,p.common_name FROM tasks t JOIN plants p ON p.id=t.plant_id WHERE t.due_date=? AND t.completed=0 ORDER BY t.kind",(date.today().isoformat(),)); return [dict(r) for r in rows]
    def complete_task(self,tid): self.conn.execute("UPDATE tasks SET completed=1 WHERE id=?",(tid,)); self.conn.commit()
