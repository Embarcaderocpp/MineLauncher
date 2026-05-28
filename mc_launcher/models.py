from pydantic import BaseModel
from enum import Enum
from typing import Optional, List
from datetime import datetime
from typing import Optional

class ModLoaderType(str, Enum):
    VANILLA = "vanilla"
    FABRIC = "fabric"
    QUILT = "quilt"
    FORGE = "forge"
    NEOFORGE = "neoforge"

class Instance(BaseModel):
    name: str
    version: str
    modloader: ModLoaderType = ModLoaderType.VANILLA
    modloader_version: Optional[str] = None
    nickname: str = "CrackedPlayer"
    jvm_args: List[str] = []
    ram_mb: int = 2048
    created_at: datetime = datetime.now()
    last_played: Optional[datetime] = None
