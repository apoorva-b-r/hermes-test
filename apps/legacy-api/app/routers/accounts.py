from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/accounts")


@router.get("")
def get_accounts():
    return [{"account_id": "acc_001", "status": "active"}]


@router.get("/{account_id}")
def get_account(account_id: str):
    return {"account_id": account_id, "status": "active"}


@router.post("/sync", deprecated=True, status_code=202)
def sync_accounts():
    return {"synced": True}
