from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.schemas import EvaluationRunRequest, EvaluationRunResponse, OverviewResponse
from app.infrastructure.database.session import get_db
from app.services.evaluation.service import EvaluationService

router = APIRouter(tags=["evaluations"])


@router.get("/overview", response_model=OverviewResponse)
def overview(db: Session = Depends(get_db)) -> OverviewResponse:
    service = EvaluationService(db)
    stats = service.get_overview_stats()
    return OverviewResponse(**stats)


@router.get("/evaluations")
def list_evaluations(db: Session = Depends(get_db)) -> list[dict]:
    service = EvaluationService(db)
    return service.list_runs()


@router.post("/evaluations/run", response_model=EvaluationRunResponse)
async def run_evaluation(
    body: EvaluationRunRequest,
    db: Session = Depends(get_db),
) -> EvaluationRunResponse:
    service = EvaluationService(db)
    result = await service.run_batch(body.strategy_name)
    return EvaluationRunResponse(**result)
