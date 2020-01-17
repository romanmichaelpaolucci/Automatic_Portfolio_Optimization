import quandl
from tools.api_socket import QuandlSocket
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import risk_models
from pypfopt import expected_returns
from pypfopt import discrete_allocation


class PortfolioDataRequest:

    """ stocks = [], start_date/end_date are strings 'YYYY-MM-DD' """
    """
        Class for portfolfio optimization, downloads relevant portfolio data
        and caches it for use in optimization without saving it locally.
    """

    def __init__(self, stocks, start_date, end_date):
        QuandlSocket()
        data = quandl.get_table(
            'WIKI/PRICES',
            ticker=stocks,
            qopts={'columns': ['date', 'ticker', 'adj_close']},
            date={'gte': start_date, 'lte': end_date},
            paginate=True
            )
        df = data.set_index('date')
        self.table = df.pivot(columns='ticker')
        # By specifying col[1] in below list comprehension
        # You can select the stock names under multi-level column
        self.table.columns = [col[1] for col in self.table.columns]


class PortfolioOptimization:

    """
        Class for optimizing a historic portfolio
    """

    def __init__(self, table):
        mu = expected_returns.mean_historical_return(table)
        S = risk_models.sample_cov(table)

        # Optimise for maximal Sharpe ratio
        ef = EfficientFrontier(mu, S)
        ef.max_sharpe()  # Raw weights
        self.cleaned_weights = ef.clean_weights()
        print(self.cleaned_weights)
        ef.portfolio_performance(verbose=True)

        latest_prices = discrete_allocation.get_latest_prices(table)
        self.allocation, self.leftover = discrete_allocation.portfolio(
            self.cleaned_weights, latest_prices, total_portfolio_value=10000
        )

    def report_discrete_allocation(self):
        print(self.allocation)
        print("Funds remaining: ${:.2f}".format(self.leftover))

    def get_cleaned_weights(self):
        return self.cleaned_weights


class PortfolioReturns:

    def __init__(self, stocks, discrete_allocation, start_date, end_date):
        data = PortfolioDataRequest(stocks, start_date, end_date).table
        self.start_date = start_date
        self.end_date = end_date
        starting_value = 0
        ending_value = 0
        for stock in stocks:
            try:
                # Initial value of portfolio
                starting_value += data[stock][0]*discrete_allocation[stock]
                # Ending portfolio value
                ending_value += \
                    data[stock][len(data[stock])-1]*discrete_allocation[stock]
            except KeyError:
                print(stock, ' received a weight of zero.')
                continue
        self.returns = [(ending_value - starting_value) / starting_value]

    def report_returns(self):
        print(
            'Portfolio Returns for ', self.start_date, ' to ', self.end_date,
            ' are ', self.returns
            )


# TODO: Create portfolio optimization pipeline
class Pipeline:
    def __init__(self, stocks):
        """
        # Almost deprecated implementation of portfolio portfolio_tools
        # This is a manual implementation of Pipeline
        if __name__ == '__main__':
            stocks = 'SYK ILMN CI CVS AMZN AAPL'.split()
            data = PortfolioDataRequest(
                    stocks,
                    '2017-01-01',
                    '2018-01-01'
                    )
            optimization = PortfolioOptimization(data.table)
            data = PortfolioDataRequest(
                    stocks,
                    '2018-01-01',
                    '2019-01-01'
                    )
            optimization = PortfolioOptimization(data.table)
            returns = PortfolioReturns(
                    stocks,
                    optimization.allocation,
                    '2018-01-01',
                    '2019-01-01'
                    )
            returns.report_returns()
        """
        pass
