import pprint
import requests
from datetime import datetime

token_address = "0x6982508145454Ce325dDbE47a25d4ec3d2311933"
last_timestamp = int(datetime.now().timestamp()) - 3600

API_TOKEN = "a5d86f543f07abf8b594170fda1ef9d2"


query = """
{
  pools(where: { token0: "0x6982508145454ce325ddbe47a25d4ec3d2311933", token1: "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2" }) {
    id
    token0 {
      id
      symbol
    }
    token1 {
      id
      symbol
    }
    liquidity
    volumeUSD
  }
}
"""



response = requests.post(
    f"https://gateway.thegraph.com/api/{API_TOKEN}/subgraphs/id/5zvR82QoaXYFyDEKLZ9t6v9adgnptxYpKpSbxtgVENFV",
    json={"query": query},
)

data = response.json()

first_pool = data["data"]["pools"][0]["id"]






query = """
query($poolId: ID!, $timestamp: BigInt!) {
  pools(where: {id: $poolId}) {
    id
    token0 {
      symbol
    }
    token1 {
      symbol
    }
    swaps(first: 20, orderBy: timestamp, orderDirection: desc, where: {timestamp_gt: $timestamp}) {
      id
      amount0
      amount1
      timestamp
      transaction {
        id
      }
      sender
    }
  }
}

"""
print(first_pool)

variables = {"tokenAddress": token_address, "timestamp": last_timestamp, "poolId": first_pool}



response = requests.post(
    f"https://gateway.thegraph.com/api/{API_TOKEN}/subgraphs/id/5zvR82QoaXYFyDEKLZ9t6v9adgnptxYpKpSbxtgVENFV",
    json={"query": query, "variables": variables},
)

data = response.json()
# if "errors" in data:
#     print("Errors:", data["errors"])
# else:
#     swaps = data["data"]["swaps"]
#     for swap in swaps:
#         print(
#             f"Sender: {swap['sender']}, Amount 0: {swap['amount0']}, Amount 1: {swap['amount1']}, Timestamp: {swap['timestamp']}, Transaction ID: {swap['transaction']['id']}"
#         )

pprint.pprint(data)






