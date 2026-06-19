from pycoingecko import CoinGeckoAPI

cg = CoinGeckoAPI()


class CoinDataFetcher:

    @staticmethod
    def get_coin_data(coin_id):

        return cg.get_coin_by_id(
            coin_id,
            localization=False,
            tickers=False,
            market_data=True,
            community_data=False,
            developer_data=True,
            sparkline=False
        )
