from dataclasses import dataclass
from datetime import datetime
import logging
import pprint
from httpx import AsyncClient
from entity.exc import FetchingPoolsError
from entity.uniswap import Pool, Swap

logger = logging.getLogger("UniSwapBot")


@dataclass
class UniSwapAPIClient:
    api_key: str
    subgraph_id: str
    http_client: AsyncClient

    def __post_init__(self):
        self.url = f"https://gateway.thegraph.com/api/{self.api_key}/subgraphs/id/{self.subgraph_id}"

    async def fetch_swaps(
        self, token_address1: str, token_address2: str, min_timestamp: int
    ) -> list[Swap]:
        """Fetch swaps from Uniswap V2 subgraph."""
        query = """
        {
          swaps(where: {
            pair_: {
              token0: "%s",
              token1: "%s"
            },
            timestamp_gte: %d
          }, first: 1000, orderBy: timestamp, orderDirection: desc) {
            id
            pair {
              token0 {
                id
                symbol
              }
              token1 {
                id
                symbol
              }
            }
            amount0In
            amount0Out
            amount1In
            amount1Out
            sender
            to
            timestamp
          }
        }
        """
        formatted_query = query % (token_address1.lower(), token_address2.lower(), min_timestamp)

        response = await self.http_client.post(
            self.url, json={'query': formatted_query}
        )
        response.raise_for_status()
        data = response.json()
        swaps = [
            Swap(
                sender=swap["sender"],
                pair=f"{swap['pair']['token0']['symbol']}-{swap['pair']['token1']['symbol']}",
                amount0=-float(swap["amount0In"]) if float(swap["amount0In"]) > 0 else float(swap["amount0Out"]),
                amount1=float(swap["amount1Out"]) if float(swap["amount0In"]) > 0 else -float(swap["amount1In"]),
                timestamp=int(swap["timestamp"]),
                id=swap["id"],
            )
            for swap in data["data"]["swaps"]
        ]

        return swaps
