from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/debug")

@router.get("/config")
def get_debug_config():
    return {
        "region": "eu-west-2",
        "feature_flags": {
            "new_ledger": False
        }
    }

