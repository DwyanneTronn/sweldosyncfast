from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from sqlmodel import Session, select
from app.database import get_session
from app.models import Tenant

api_key_header = APIKeyHeader(name="X-API-Key")

async def get_current_tenant(
    api_key: str = Security(api_key_header),
    db: Session = Depends(get_session)
) -> Tenant:
    # 1. Fetch Tenant
    statement = select(Tenant).where(Tenant.api_key == api_key)
    tenant = db.exec(statement).first()
    
    # 2. Check if active
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )
    
    if not tenant.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant is inactive",
        )
        
    return tenant
