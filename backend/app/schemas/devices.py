from pydantic import BaseModel, Field


class DeviceHeartbeatRequest(BaseModel):
    device_id: str = Field(min_length=8, max_length=100)
    device_name: str | None = Field(default=None, max_length=160)
    platform: str | None = Field(default=None, max_length=120)
    browser: str | None = Field(default=None, max_length=120)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    location_accuracy: float | None = Field(default=None, ge=0, le=100000)
    location_permission: str = Field(
        default="unknown",
        pattern="^(unknown|granted|denied|unavailable|ip)$",
    )
