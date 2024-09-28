import asyncio
import logging
from core.ioc import get_container
from entity.uniswap import Competition, CompetitionSwap, TopWalletHolder
from service.competition_service import CompetitionService
from redis.asyncio.client import Redis
import asyncio

from service.notifier import TelegramNotifier

logger = logging.getLogger("UniSwapBot")


def generate_text_from_swap(
    competition_swap: CompetitionSwap, competition: Competition
) -> str:
    first_pair, second_pair = competition_swap.swap.pair.split("-")

    spent_amount = abs(competition_swap.swap.amount1)

    money_emoji = "📊" * min(int(spent_amount / 0.005), 60)

    if len(money_emoji) == 0:
        money_emoji = "💸"

    return (
        f"🪙 NEW BUY: {competition.name}\n\n" 
        f"{money_emoji}\n\n"
        f"🔋 Got <b>{competition_swap.swap.amount0} {first_pair}</b>\n"
        f"🔋 Spent <b>{spent_amount} {second_pair}</b>\n\n"
        f"🪙 Wallet:"
        f" <blockquote>{competition_swap.swap.sender}</blockquote>"
    )



async def _process_competitions(competition: Competition) -> None:
    container = get_container()

    async with container() as container_r:
        notifier: TelegramNotifier = await container_r.get(TelegramNotifier)
        service: CompetitionService = await container_r.get(CompetitionService)

        swaps = await service.fetch_swaps(competition)
        for swap in swaps:
            if swap.swap.amount0 > 0:
                notification = generate_text_from_swap(swap, competition)
                explore_button_link = (
                    f"https://dexscreener.com/ethereum/{competition.token_address}"
                )
                image_url = "https://ibb.co/86wwqSN"
                await notifier.notify(
                    chat_id=competition.channel_id,
                    text=notification,
                    photo_url=image_url,
                    button_url=explore_button_link,
                )


async def process_competitions(competition: Competition) -> None:
    container = get_container()
    redis: Redis = await container.get(Redis)

    competition_key = f"competition:{competition.id}"

    is_locked = await redis.setnx(competition_key, "locked")
    if not is_locked:
        return
    
    logger.info(f"Processing competition {competition.id}")

    await redis.expire(competition_key, 100)

    try:
        await _process_competitions(competition)
    finally:
        await redis.delete(competition_key)


async def fetch_updates_in_background() -> None:
    container = get_container()

    while True:
        try:
            async with container() as container_r:
                service: CompetitionService = await container_r.get(CompetitionService)
                competitions = await service.get_all_competitions()
                if competitions is None:
                    logger.warning("No competitions found")
                    continue

                coro = [process_competitions(competition) for competition in competitions]
                await asyncio.gather(*coro)

        except Exception as e:
            logger.error(f"Error occurred in fetch updates loop: {e}")

        await asyncio.sleep(30)


def generate_text_from_top_wallet_holder(
    competition: Competition, top_wallet_holder: TopWalletHolder) -> str:
    main_pair = top_wallet_holder.pair.split("-")[0]
    return (
        f"🏆 <b>We have a winner in:</b> <code>{competition.name}</code>\n\n"
        f"💰 <b>Total Amount:</b> {top_wallet_holder.total_amount} <b>{main_pair}</b>\n"
        f"👛 <b>Wallet Address:</b> <blockquote>{top_wallet_holder.wallet_address}</blockquote>\n\n"
        f"🎉 <b>Congratulations!</b> 🥳 Your rewards will be credited shortly!"
    )



async def process_top_wallet_holders() -> None:
    container = get_container()
    redis: Redis = await container.get(Redis)
    

    while True:
        try:
            async with container() as container_r:
                service: CompetitionService = await container_r.get(CompetitionService)
                competitions = await service.get_all_competitions_that_expired()

                for competition in competitions:

                    is_locked = await redis.setnx(f"top_wallet_holder:{competition.id}", "locked")
                    if not is_locked:
                        continue

                    logger.info(f"Processing top wallet holder for {competition.id}")

                    await redis.expire(f"top_wallet_holder:{competition.id}", 100)

                    try:
                        top = await service.get_top_wallet_holder(competition.id)

                        if top:
                            await service.mark_competition_as_completed(competition.id, top.wallet_address)

                            notifier: TelegramNotifier = await container.get(TelegramNotifier)
                            photo_url="https://ibb.co/hMPNrYh"

                            await notifier.notify(
                                chat_id=competition.channel_id,
                                text=generate_text_from_top_wallet_holder(competition, top),
                                photo_url=photo_url
                        )

                    finally:
                        await redis.delete(f"top_wallet_holder:{competition.id}")

        except Exception as e:
            logger.error(f"Error occurred in process top wallet holders loop: {e}")

        await asyncio.sleep(60)
