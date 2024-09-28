from http.client import HTTPException
from fastapi import APIRouter, status
from dishka import FromDishka
from dishka.integrations.fastapi import inject


from entity.uniswap import Competition
from presentation.api.uniswap.competitions.schemas import CreateCompetitionRequestSchema, CreateCompetitionResponseSchema, GetTopWalletHolderResponseSchema
from presentation.api.uniswap.exc import ErrorResponseSchema
from service.competition_service import CompetitionService


router = APIRouter(tags=["competitions"])

@router.post(
    "/",
    description="Create competition",
    responses={
        status.HTTP_201_CREATED: {"model": CreateCompetitionResponseSchema},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponseSchema},
    },
)
@inject
async def create_competition(
        schema: CreateCompetitionRequestSchema,
        service: FromDishka[CompetitionService],
    ):

    competition = await service.add_competition(
        Competition(
            user_id=schema.user_id,
            channel_id=schema.channel_id,
            name=schema.competition_name,
            start_date=schema.start_date,
            end_date=schema.end_date,
            token_address=schema.token_address,
        )
    )

    return CreateCompetitionResponseSchema(competition_id=competition.id)

@router.get("/{competition_id}/top",
    description="Get top wallet holder",
    responses={
        status.HTTP_200_OK: {"model": GetTopWalletHolderResponseSchema},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponseSchema},
    },
)
@inject
async def get_top_wallet(competition_id: int, service: FromDishka[CompetitionService]):
    top_wallet = await service.get_top_wallet_holder(competition_id)
    if not top_wallet:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="{error: 'No Swaps found'}")
    return GetTopWalletHolderResponseSchema(top_wallet_holder=top_wallet.wallet_address, total_amount=top_wallet.total_amount)