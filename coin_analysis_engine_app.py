from dataclasses import dataclass

from coin_data import CoinDataFetcher

@dataclass
class CoinMetrics:

    name: str
    current_price: float
    ath_price: float
    market_cap: float
    market_cap_rank: int

    circulating_supply: float = 0
    total_supply: float = 0

    github_stars: int = 0
    github_commits: int = 0


class CoinAnalysisEngineApp:

    def __init__(self, coin_id):

        self.coin_id = coin_id

        self.metrics = self.load_metrics()
    
    def load_metrics(self):

        data = CoinDataFetcher.get_coin_data(
        self.coin_id
        )

        market = data["market_data"]

        developer = data["developer_data"]

        return CoinMetrics(

            name=data["name"],

            current_price=market["current_price"]["usd"],

            ath_price=market["ath"]["usd"],

            market_cap=market["market_cap"]["usd"],

            market_cap_rank=data["market_cap_rank"],

            github_stars=developer.get("stars", 0),

            github_commits=developer.get("commit_count_4_weeks", 0)
        )
    

    @property
    def drawdown(self):

        return (
        (
            self.metrics.ath_price
            -
            self.metrics.current_price
        )
        /
        self.metrics.ath_price
        ) * 100
    
    #@property
    #def score_drawdown(self):

    #    dd = self.drawdown

    #   if dd > 90:
    #        return 10


    @property
    def supply_ratio(self):

        if self.metrics.total_supply == 0:
            return 1

        return (
        self.metrics.circulating_supply
        /
        self.metrics.total_supply
    )


    def score_drawdown(self):

        dd = self.drawdown

        if dd > 90:
            return 10

        elif dd > 80:
            return 8

        elif dd > 70:
            return 6

        return 4

    def score_rank(self):

        rank = self.metrics.market_cap_rank

        if rank is None:
            return 4

        if rank <= 10:
            return 10

        elif rank <= 25:
            return 8

        elif rank <= 50:
            return 6
        return 4

    #@property
    def score_supply(self):

        ratio = self.supply_ratio

        if ratio > 0.90:
            return 10

        elif ratio > 0.75:
            return 8

        elif ratio > 0.50:
            return 6

        return 4

    #@property
    def score_development(self):

        commits = self.metrics.github_commits

        if commits > 500:
            return 10

        elif commits > 100:
            return 8

        return 6

    
    def score_quality(self):

        rank = self.metrics.market_cap_rank

        if rank <= 3:
            return 10

        elif rank <= 10:
            return 9

        elif rank <= 20:
            return 8

        elif rank <= 50:
            return 6

        elif rank <= 100:
            return 4

        return 2
    
    def quality_score(self):

        score = (

            self.score_quality() * 0.50 +

            self.score_development() * 0.30 +

            self.score_rank() * 0.20

        )
        return round(score, 2)

    def valuation_score(self):

        score = (

            self.score_drawdown() * 0.70 +

            self.score_supply() * 0.30

        )

        return round(score, 2)
    

    def final_score(self):

        score = (

            self.quality_score() * 0.60 +

            self.valuation_score() * 0.40

        )

        return round(score, 2)
 


    def conviction_level(self):
        quality = self.quality_score()
        valuation = self.valuation_score()

        if quality >= 8.5 and valuation >= 8:
            return "STRONG BUY"

        elif quality >= 8:
            return "HIGH QUALITY"

        elif valuation >= 8:
            return "DEEP VALUE"

        elif quality >= 7 and valuation >= 7:
            return "MODERATE BUY"

        return "SPECULATIVE"


    def verdict(self):

        score = self.final_score()

        if score >= 8:
            return "ACCUMULATE"

        elif score >= 7:
            return "BUY"

        elif score >= 6:
            return "HOLD"

        return "AVOID"
    
    
    def report(self):

        print("\n" + "=" * 60)

        print(
            f"{self.metrics.name.upper()} "
            f"COIN REPORT"
        )

        print("=" * 60)

        print(
            f"Current Price      : "
            f"${self.metrics.current_price:,.2f}"
        )   

        print(
            f"ATH Price          : "
            f"${self.metrics.ath_price:,.2f}"
        )

        print(
            f"ATH Drawdown       : "
            f"{self.drawdown:.2f}%"
        )

        print(
            f"Market Cap Rank    : "
            f"{self.metrics.market_cap_rank}"
        )

        print(
            f"GitHub Commits     : "
            f"{self.metrics.github_commits}"
        )

        print("-" * 60)

        
        print(
            f"Quality Score      : "
            f"{self.quality_score()}/10"
        )

        print(
            f"Valuation Score    : "
            f"{self.valuation_score()}/10"
        )

        
        print(
            f"Conviction Level   : "
            f"{self.conviction_level()}"
        )

        print(
            f"Investment Score   : "
            f"{self.final_score()}/10"
        )


        print(
            f"Verdict            : "
            f"{self.verdict()}"
        )

        print("=" * 60)
    

