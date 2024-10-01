from fastapi import APIRouter, status, HTTPException
from dishka import FromDishka
from dishka.integrations.fastapi import inject


from entity.uniswap import Competition
from presentation.api.uniswap.competitions.schemas import (
    CreateCompetitionRequestSchema,
    CreateCompetitionResponseSchema,
    GetTopWalletHolderResponseSchema,
)
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
    create_competition_request: CreateCompetitionRequestSchema,
    competition_service: FromDishka[CompetitionService],
) -> CreateCompetitionResponseSchema:
    """
    Create a new competition.
    """

    competition = Competition(
        user_id=create_competition_request.user_id,
        channel_id=create_competition_request.channel_id,
        name=create_competition_request.competition_name,
        start_date=create_competition_request.start_date,
        end_date=create_competition_request.end_date,
        token_address=create_competition_request.token_address,
    )

    created_competition = await competition_service.add_competition(competition)

    return CreateCompetitionResponseSchema(competition_id=created_competition.id)


@router.get(
    "/{channel_id}/top/{top}",
    responses={
        status.HTTP_200_OK: {"model": list[GetTopWalletHolderResponseSchema]},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponseSchema},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponseSchema},
    },
)
@inject
async def get_top_wallet_holders(
    channel_id: int, top: int, service: FromDishka[CompetitionService]
) -> list[GetTopWalletHolderResponseSchema]:
    """
    Return top top wallet holders for a given competition.
    """
    if top <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Top must be greater than 0"},
        )

    competition = await service.get_competition_by_channel_id(channel_id)

    top_wallet_holders = await service.get_top_wallet_holders(competition.id, top)

    if not top_wallet_holders:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "No wallet holders found"},
        )

    return GetTopWalletHolderResponseSchema.from_entity(top_wallet_holders)
