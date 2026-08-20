from dataclasses import dataclass, asdict
from typing import Optional
@dataclass
class PlantCreate:
    common_name:str; scientific_name:Optional[str]=None; family:Optional[str]=None; variety:Optional[str]=None
    location:Optional[str]=None; sun_exposure:Optional[str]=None; watering_frequency_days:int=7; flowering_months:Optional[str]=None
    pruning_months:Optional[str]=None; fertilizing_months:Optional[str]=None; notes:Optional[str]=None; trefle_id:Optional[int]=None
    @classmethod
    def from_dict(cls,d):
        if not d.get("common_name"): raise ValueError("common_name est requis")
        allowed={k:v for k,v in d.items() if k in cls.__dataclass_fields__}; return cls(**allowed)
@dataclass
class Plant(PlantCreate):
    id:int=0; created_at:str=""; updated_at:str=""
    def to_dict(self): return asdict(self)
