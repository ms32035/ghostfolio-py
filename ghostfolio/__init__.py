import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union

import requests
from requests.exceptions import HTTPError


class Ghostfolio:
    """
    A Python client for the Ghostfolio API.

    Ghostfolio is an open-source wealth management software that helps you track
    your personal finances and investments. This client provides a Python interface
    to interact with the Ghostfolio API.

    Args:
        token (str): Your Ghostfolio access token
        host (str): The Ghostfolio instance URL (defaults to https://ghostfol.io/)

    Example:
        ```python
        from ghostfolio import Ghostfolio

        # Initialize client
        client = Ghostfolio(token="your_access_token")

        # Get portfolio performance
        performance = client.performance(date_range="1y")

        # Get account details
        accounts = client.accounts()
        ```

    Attributes:
        host (str): The Ghostfolio instance URL
        token (str): Your Ghostfolio access token
    """

    def __init__(
        self, token: str, host: str = "https://ghostfol.io/", verify_ssl: bool = True
    ):
        """
        Initialize the Ghostfolio client.

        Args:
            token (str): Your Ghostfolio access token
            host (str): The Ghostfolio instance URL
            verify_ssl (bool): Whether to verify SSL certificates
        """
        self.host = host
        self._token = token
        self._jwt_token: str | None = None
        self._jwt_token_expiry: datetime | None = None
        self._verify_ssl = verify_ssl

    def _url(
        self, endpoint: str, object_id: str | None = None, api_version: str = "v1"
    ) -> str:
        """
        Build API URL for given endpoint.

        Args:
            endpoint (str): API endpoint path
            object_id (Optional[str]): Optional object ID for the endpoint
            api_version (str): API version (default: "v1")

        Returns:
            str: Complete API URL
        """
        return f"{self.host}/api/{api_version}/{endpoint}/" + (
            object_id + "/" if object_id else ""
        )

    def _refresh_jwt_token(self) -> None:
        """
        Refresh JWT token if expired or not present.

        This method handles the authentication flow by obtaining a JWT token
        from the Ghostfolio API using the provided access token.
        """
        if self._jwt_token is not None and self._jwt_token_expiry < datetime.now():
            return

        self._jwt_token = self._process_response(
            requests.post(
                f"{self.host}/api/v1/auth/anonymous/",
                {"accessToken": self._token},
                verify=self._verify_ssl,
            )
        )["authToken"]
        self._jwt_token_expiry = datetime.now() + timedelta(days=30)

    def get(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        api_version: str = "v1",
    ) -> dict[str, Any]:
        """
        Make a GET request to the Ghostfolio API.

        Args:
            endpoint (str): API endpoint path
            params (Optional[Dict[str, Any]]): Query parameters to include in the request
            api_version (str): API version (default: "v1")

        Returns:
            Dict[str, Any]: API response as dictionary

        Raises:
            HTTPError: If the request fails or returns an error status code
        """
        self._refresh_jwt_token()

        return self._process_response(
            requests.get(
                self._url(endpoint, api_version=api_version),
                headers={"Authorization": f"Bearer {self._jwt_token}"},
                params=params,
                verify=self._verify_ssl,
            )
        )

    def post(
        self,
        endpoint: str,
        data: dict[str, Any] | None = None,
        api_version: str = "v1",
        object_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Make a POST request to the Ghostfolio API.

        Args:
            endpoint (str): API endpoint path
            data (Optional[Dict[str, Any]]): Request body data to send
            api_version (str): API version (default: "v1")
            object_id (Optional[str]): Optional object ID for the endpoint

        Returns:
            Dict[str, Any]: API response as dictionary

        Raises:
            HTTPError: If the request fails or returns an error status code
        """
        self._refresh_jwt_token()

        return self._process_response(
            requests.post(
                self._url(endpoint, object_id, api_version),
                headers={"Authorization": f"Bearer {self._jwt_token}"},
                json=data,
                verify=self._verify_ssl,
            )
        )

    def put(
        self,
        endpoint: str,
        data: dict[str, Any] | None = None,
        api_version: str = "v1",
        object_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Make a PUT request to the Ghostfolio API.

        Args:
            endpoint (str): API endpoint path
            data (Optional[Dict[str, Any]]): Request body data to send
            api_version (str): API version (default: "v1")
            object_id (Optional[str]): Optional object ID for the endpoint

        Returns:
            Dict[str, Any]: API response as dictionary

        Raises:
            HTTPError: If the request fails or returns an error status code
        """
        self._refresh_jwt_token()

        return self._process_response(
            requests.put(
                self._url(endpoint, object_id, api_version),
                headers={"Authorization": f"Bearer {self._jwt_token}"},
                json=data,
                verify=self._verify_ssl,
            )
        )

    @staticmethod
    def _process_response(resp: requests.Response) -> dict[str, Any]:
        """
        Process API response and handle errors.

        Args:
            resp (requests.Response): HTTP response object from requests library

        Returns:
            Dict[str, Any]: JSON response data as dictionary

        Raises:
            HTTPError: If the request failed or returned an error status code
        """
        try:
            resp.raise_for_status()
        except HTTPError as http_err:
            logging.error(resp.text)
            raise http_err

        return resp.json()

    def orders(self, account_id: str | None = None) -> dict[str, Any]:
        """
        Get all orders from your portfolio.

        Retrieves a list of all buy/sell orders in your portfolio, optionally
        filtered by a specific account.

        Args:
            account_id (Optional[str]): Optional account ID to filter orders by specific account

        Returns:
            Dict[str, Any]: Dictionary containing order data with activities, pagination, etc.

        Example:
            ```python
            # Get all orders
            orders = client.orders()

            # Get orders for specific account
            account_orders = client.orders(account_id="account_123")
            ```
        """
        params = {"accounts": account_id} if account_id else None
        return self.get("order", params=params)

    def performance(self, date_range: str = "max") -> dict[str, Any]:
        """
        Get portfolio performance data.

        Retrieves comprehensive performance metrics for your portfolio including
        returns, benchmarks, and performance comparisons over the specified time period.

        Args:
            date_range (str): Time range for performance data. Options include:
                - "1d": 1 day
                - "1w": 1 week
                - "1m": 1 month
                - "3m": 3 months
                - "6m": 6 months
                - "1y": 1 year
                - "2y": 2 years
                - "5y": 5 years
                - "max": Maximum available period

        Returns:
            Dict[str, Any]: Dictionary containing performance metrics including:
                - returns: Portfolio returns data
                - benchmarks: Benchmark comparison data
                - performance: Detailed performance metrics
                - range: The date range used

        Example:
            ```python
            # Get 1 year performance
            perf = client.performance(date_range="1y")

            # Get maximum available performance data
            max_perf = client.performance()
            ```
        """
        return self.get(
            "portfolio/performance", params={"range": date_range}, api_version="v2"
        )

    def holdings(self, date_range: str = "max") -> dict[str, Any]:
        """
        Get portfolio holdings and positions.

        Retrieves current portfolio holdings including positions, allocations,
        and asset breakdowns for the specified time period.

        Args:
            date_range (str): Time range for holdings data. Options include:
                - "1d": 1 day
                - "1w": 1 week
                - "1m": 1 month
                - "3m": 3 months
                - "6m": 6 months
                - "1y": 1 year
                - "2y": 2 years
                - "5y": 5 years
                - "max": Maximum available period

        Returns:
            Dict[str, Any]: Dictionary containing holdings data including:
                - holdings: List of current positions
                - accounts: Account breakdown
                - allocations: Asset allocation data
                - range: The date range used

        Example:
            ```python
            # Get current holdings
            holdings = client.holdings()

            # Get holdings for specific period
            monthly_holdings = client.holdings(date_range="1m")
            ```
        """
        return self.get("portfolio/holdings", params={"range": date_range})

    def position(self, data_source: str, symbol: str) -> dict[str, Any]:
        """
        Get position details for a specific symbol from a data source.

        Retrieves detailed information about a specific position including
        current value, quantity, performance, and market data.

        Args:
            data_source (str): Data source (e.g., "YAHOO", "COINGECKO", "MANUAL")
            symbol (str): Symbol/ticker of the asset

        Returns:
            Dict[str, Any]: Dictionary containing position details including:
                - symbol: Asset symbol
                - quantity: Current quantity held
                - value: Current market value
                - performance: Performance metrics
                - marketData: Current market data

        Example:
            ```python
            # Get position for Microsoft stock
            msft_position = client.position("YAHOO", "MSFT")

            # Get position for Bitcoin
            btc_position = client.position("COINGECKO", "bitcoin")
            ```
        """
        return self.get(f"portfolio/position/{data_source}/{symbol}")

    def import_transactions(self, data: dict[str, Any]) -> None:
        """
        Import transactions into your portfolio.

        Imports a batch of transactions (buy/sell orders) into your Ghostfolio
        portfolio. This is useful for bulk importing historical data or
        transactions from other platforms.

        Args:
            data (Dict[str, Any]): Transaction data in the format expected by Ghostfolio API.
                Should contain an "activities" list with transaction objects.

        Raises:
            HTTPError: If the import fails or returns an error status code

        Example:
            ```python
            transactions = {
                "activities": [
                    {
                        "currency": "USD",
                        "dataSource": "YAHOO",
                        "date": "2021-09-15T00:00:00.000Z",
                        "fee": 19,
                        "quantity": 5,
                        "symbol": "MSFT",
                        "type": "BUY",
                        "unitPrice": 298.58
                    }
                ]
            }
            client.import_transactions(transactions)
            ```
        """
        self.post("import", data)

    def details(self) -> dict[str, Any]:
        """
        Get comprehensive portfolio details including accounts, positions, and summary.

        Retrieves a complete overview of your portfolio including account
        information, current positions, performance summary, and portfolio metrics.

        Returns:
            Dict[str, Any]: Dictionary containing complete portfolio information including:
                - accounts: List of all accounts
                - positions: Current portfolio positions
                - summary: Portfolio summary metrics
                - performance: Overall performance data

        Example:
            ```python
            # Get all portfolio details
            details = client.details()
            ```
        """
        return self.get("portfolio/details")

    def investments(
        self, group_by: str = "month", date_range: str = "max"
    ) -> dict[str, Any]:
        """
        Get investment data grouped by time period.

        Retrieves investment activity data grouped by the specified time period,
        showing cash flows, contributions, and investment patterns over time.

        Args:
            group_by (str): Grouping period ("day", "week", "month", "quarter", "year")
            date_range (str): Time range for investment data. Options include:
                - "1d": 1 day
                - "1w": 1 week
                - "1m": 1 month
                - "3m": 3 months
                - "6m": 6 months
                - "1y": 1 year
                - "2y": 2 years
                - "5y": 5 years
                - "max": Maximum available period

        Returns:
            Dict[str, Any]: Dictionary containing investment data grouped by the specified period including:
                - investments: List of investment periods with data
                - total: Total investment amount
                - range: The date range used
                - groupBy: The grouping period used

        Example:
            ```python
            # Get monthly investments for the last year
            investments = client.investments(group_by="month", date_range="1y")

            # Get quarterly investments for maximum period
            quarterly = client.investments(group_by="quarter")
            ```
        """
        return self.get(
            "portfolio/investments", params={"range": date_range, "groupBy": group_by}
        )

    def dividends(
        self, group_by: str = "month", date_range: str = "max"
    ) -> dict[str, Any]:
        """
        Get dividend data grouped by time period.

        Retrieves dividend income data grouped by the specified time period,
        showing dividend payments, yield, and income patterns over time.

        Args:
            group_by (str): Grouping period ("day", "week", "month", "quarter", "year")
            date_range (str): Time range for dividend data. Options include:
                - "1d": 1 day
                - "1w": 1 week
                - "1m": 1 month
                - "3m": 3 months
                - "6m": 6 months
                - "1y": 1 year
                - "2y": 2 years
                - "5y": 5 years
                - "max": Maximum available period

        Returns:
            Dict[str, Any]: Dictionary containing dividend data grouped by the specified period including:
                - dividends: List of dividend periods with data
                - total: Total dividend income
                - range: The date range used
                - groupBy: The grouping period used

        Example:
            ```python
            # Get monthly dividends for the last year
            dividends = client.dividends(group_by="month", date_range="1y")

            # Get quarterly dividends for maximum period
            quarterly = client.dividends(group_by="quarter")
            ```
        """
        return self.get(
            "portfolio/dividends", params={"range": date_range, "groupBy": group_by}
        )

    def accounts(self) -> dict[str, Any]:
        """
        Get all accounts in your portfolio.

        Retrieves a list of all accounts in your portfolio including account
        types, balances, and account-specific information.

        Returns:
            Dict[str, Any]: Dictionary containing account information including:
                - accounts: List of all accounts
                - total: Total portfolio value across all accounts
                - currency: Base currency for the portfolio

        Example:
            ```python
            # Get all accounts
            accounts = client.accounts()
            ```
        """
        return self.get("account")

    def market_data_admin(self) -> dict[str, Any]:
        """
        Get overview of market data loaded in your Ghostfolio instance.

        Retrieves an administrative overview of market data sources and
        symbols that are currently loaded in your Ghostfolio instance.
        This is useful for understanding what market data is available.

        Returns:
            Dict[str, Any]: Dictionary containing market data overview including:
                - dataSources: List of available data sources
                - symbols: List of symbols with market data
                - lastUpdate: Last update timestamp

        Example:
            ```python
            # Get market data overview
            market_data = client.market_data_admin()
            ```
        """
        return self.get("admin/market-data")

    def market_data(self, data_source: str, symbol: str) -> dict[str, Any]:
        """
        Get market data for a specific symbol from a data source.

        Retrieves current market data for a specific symbol including price,
        volume, market cap, and other relevant market information.

        Args:
            data_source (str): Data source (e.g., "YAHOO", "COINGECKO", "MANUAL")
            symbol (str): Symbol/ticker of the asset

        Returns:
            Dict[str, Any]: Dictionary containing market data for the specified symbol including:
                - symbol: Asset symbol
                - price: Current market price
                - currency: Price currency
                - marketData: Additional market data (volume, market cap, etc.)
                - dataSource: Source of the market data

        Example:
            ```python
            # Get market data for Apple stock
            aapl_data = client.market_data("YAHOO", "AAPL")

            # Get market data for Ethereum
            eth_data = client.market_data("COINGECKO", "ethereum")
            ```
        """
        return self.get(f"admin/market-data/{data_source}/{symbol}")

    def __hash__(self) -> int:
        """
        Return hash based on token and host.

        Returns:
            int: Hash value based on token and host combination
        """
        return hash((self._token, self.host))

    def __repr__(self) -> str:
        """
        Return string representation of the client.

        Returns:
            str: String representation showing the host URL
        """
        return f"Ghostfolio(host={self.host})"
