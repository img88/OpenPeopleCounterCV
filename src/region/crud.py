import uuid
from datetime import datetime
from src.database.base_database import BaseDatabase
from .schema import RegionCreate, RegionUpdate

def create_region(db: BaseDatabase, data: RegionCreate):
    region_id = str(uuid.uuid4())
    query = """
    INSERT INTO region_registry (
        pk_region_id, region_name, region_description, polygon, created_at, updated_at
    ) VALUES (%s, %s, %s, %s, %s, %s)
    """
    now = datetime.utcnow()
    db.execute_query(query, (
        region_id,
        data.region_name,
        data.region_description,
        data.polygon,
        now,
        now
    ))
    return region_id

def get_region(db: BaseDatabase, region_id: str):
    query = "SELECT * FROM region_registry WHERE pk_region_id = %s"
    result = db.execute_query(query, (region_id,))
    return result[0] if result else None

def get_all_regions(db: BaseDatabase):
    query = "SELECT * FROM region_registry ORDER BY created_at DESC"
    return db.execute_query(query)

def update_region(db: BaseDatabase, region_id: str, data: RegionUpdate):
    query = """
    UPDATE region_registry
    SET region_name = %s,
        region_description = %s,
        polygon = %s,
        updated_at = %s
    WHERE pk_region_id = %s
    """
    db.execute_query(query, (
        data.region_name,
        data.region_description,
        data.polygon,
        datetime.utcnow(),
        region_id
    ))

def delete_region(db: BaseDatabase, region_id: str):
    query = "DELETE FROM region_registry WHERE pk_region_id = %s"
    db.execute_query(query, (region_id,))
