from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from backend.app.api.dependencies import get_current_user
from backend.app.db.database import get_db
from backend.app.db.models import User, VisitorDevice
from backend.app.schemas.devices import DeviceHeartbeatRequest


router = APIRouter(tags=["Devices"])


@router.post("/device-heartbeat", status_code=202)
def device_heartbeat(
    payload: DeviceHeartbeatRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    forwarded = request.headers.get("x-forwarded-for", "").split(",", 1)[0].strip()
    client_ip = forwarded or (request.client.host if request.client else "")
    row = db.query(VisitorDevice).filter(
        VisitorDevice.device_id == payload.device_id
    ).first()
    values = payload.model_dump()
    values.pop("device_id", None)
    if row is None:
        row = VisitorDevice(device_id=payload.device_id, **values)
        db.add(row)
    else:
        row.visit_count = int(row.visit_count or 0) + 1
        row.last_seen_at = datetime.utcnow()
        for key in ("device_name", "platform", "browser", "location_permission"):
            value = values.get(key)
            if value:
                setattr(row, key, value)
        if payload.latitude is not None and payload.longitude is not None:
            row.latitude = payload.latitude
            row.longitude = payload.longitude
            row.location_accuracy = payload.location_accuracy
        elif payload.location_permission in {"denied", "unavailable"}:
            row.latitude = None
            row.longitude = None
            row.location_accuracy = None
    row.user_agent = request.headers.get("user-agent", "")[:1000]
    row.ip_address = client_ip[:64]
    db.commit()
    return {"status": "recorded"}


@router.get("/admin/devices")
def list_visitor_devices(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Chỉ admin mới xem thiết bị")
    rows = (
        db.query(VisitorDevice)
        .order_by(VisitorDevice.last_seen_at.desc())
        .limit(1000)
        .all()
    )
    return [
        {
            "id": row.id,
            "device_id": row.device_id,
            "device_name": row.device_name,
            "platform": row.platform,
            "browser": row.browser,
            "ip_address": row.ip_address,
            "latitude": row.latitude,
            "longitude": row.longitude,
            "location_accuracy": row.location_accuracy,
            "location_permission": row.location_permission,
            "visit_count": row.visit_count,
            "first_seen_at": row.first_seen_at,
            "last_seen_at": row.last_seen_at,
        }
        for row in rows
    ]
