from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/v1/accounts")

@router.api_route("", methods=["GET", "HEAD"])
def get_accounts():
    return [{"account_id": "acc_001", "status": "active"}]

@router.api_route("/{account_id}", methods=["GET", "HEAD"])
def get_account(account_id: str):
    if account_id == "sync":
        raise HTTPException(status_code=405, detail="Method Not Allowed")
    return {"account_id": account_id, "status": "active"}

@router.post("/sync", deprecated=True, status_code=202)
def sync_accounts():
    return {"synced": True}

