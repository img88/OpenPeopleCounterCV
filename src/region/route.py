from fastapi import APIRouter, Depends, HTTPException

from src.database.base_database import BaseDatabase
from src.database.database_factory import get_database_instance
from .schema import RegionCreate, RegionUpdate, RegionOut
from . import crud as crud_region

from typing import List

router = APIRouter(prefix="/regions", tags=["Regions"])

def get_db():
    return get_database_instance()

@router.post("/", response_model=str)
def create_region(data: RegionCreate, db: BaseDatabase = Depends(get_db)):
    """
    ```
    {
    "region_name": "Pintu Masuk A",
    "region_description": "Pintu utama gedung A",
    "polygon": "[[1000, 500], [1300, 500], [1300, 1000], [1000, 1000]]"
    }
    ```
    """
    return crud_region.create_region(db, data)

@router.get("/", response_model=List[RegionOut])
def list_regions(db: BaseDatabase = Depends(get_db)):
    result = crud_region.get_all_regions(db)
    return [RegionOut(**dict(zip(
        ["pk_region_id", "region_name", "region_description", "polygon", "created_at", "updated_at"], row
    ))) for row in result]

@router.get("/{region_id}", response_model=RegionOut)
def get_region(region_id: str, db: BaseDatabase = Depends(get_db)):
    row = crud_region.get_region(db, region_id)
    if not row:
        raise HTTPException(status_code=404, detail="Region not found")
    return RegionOut(**dict(zip(
        ["pk_region_id", "region_name", "region_description", "polygon", "created_at", "updated_at"], row
    )))

@router.put("/{region_id}")
def update_region(region_id: str, data: RegionUpdate, db: BaseDatabase = Depends(get_db)):
    crud_region.update_region(db, region_id, data)
    return {"message": "Region updated"}

@router.delete("/{region_id}")
def delete_region(region_id: str, db: BaseDatabase = Depends(get_db)):
    crud_region.delete_region(db, region_id)
    return {"message": "Region deleted"}
