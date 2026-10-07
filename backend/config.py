"""Configuration settings for wyoloservice2_cluster_control backend."""

import os
from typing import Optional


class Settings:
    """Cluster Control backend configuration."""

    CONTROL_HOST: str = os.getenv("CONTROL_HOST", "192.168.10.252")
    REDIS_HOST: str = os.getenv("REDIS_HOST", CONTROL_HOST)
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "23437"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD", None)

    @property
    def REDIS_URL(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # JWT Settings
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "wyolo-cluster-secret-key-production-2026")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", str(60 * 24)))

    # Initial Admin Seed
    DEFAULT_ADMIN_USER: str = os.getenv("DEFAULT_ADMIN_USER", "wisrovi")
    DEFAULT_ADMIN_PASSWORD: str = os.getenv("DEFAULT_ADMIN_PASSWORD", "wyoloservice")


settings = Settings()
