import pymssql
from config import Config

SCHEMA = """
Table: FinancialData
Columns:
- ShortName (text): company name
- Symbol (text): stock ticker
- Industry (text): industry sector
- EbitdaMargins, ProfitMargins, GrossMargins, OperatingMargins (float): margin percentages
- TotalRevenue, GrossProfits, Ebitda, FreeCashflow, OperatingCashflow (float): absolute values
- RevenueGrowth, EarningsGrowth, EarningsQuarterlyGrowth (float): growth rates
- MarketCap, EnterpriseValue, TotalCash, TotalDebt (float): valuation/balance sheet
- ReturnOnAssets, ReturnOnEquity, DebtToEquity, CurrentRatio (float): ratios
- CurrentPrice, ForwardEps, TrailingEps, BookValue, PriceToBook, ForwardPE (float): stock metrics
"""


def get_connection():
    return pymssql.connect(
        server=Config.SQL_SERVER,
        user=Config.SQL_USER,
        password=Config.SQL_PASSWORD,
        database=Config.SQL_DATABASE,
        tds_version="7.4",
    )


def run_sql_query(sql: str):
    try:
        conn = get_connection()
        cursor = conn.cursor(as_dict=True)
        cursor.execute(sql)
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception as e:
        return {"error": str(e)}
