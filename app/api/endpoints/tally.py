from fastapi import APIRouter

from app.services.tally import ClickCollector

router = APIRouter()


@router.post("/tally")
def tally_clicks():
    ClickCollector().run()
    return {"status": "clicks collected successfully"}
