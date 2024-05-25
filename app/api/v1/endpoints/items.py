from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def read_items():
    return [{"item_id": "foo"}, {"item_id": "bar"}]
