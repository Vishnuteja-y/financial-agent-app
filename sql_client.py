import pyodbc
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
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={Config.SQL_SERVER};"
        f"DATABASE={Config.SQL_DATABASE};"
        f"UID={Config.SQL_USER};"
        f"PWD={Config.SQL_PASSWORD};"
        f"Encrypt=yes;"
        f"TrustServerCertificate=no;"
    )
    return pyodbc.connect(conn_str)


def run_sql_query(sql: str):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
        conn.close()
        return [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        return {"error": str(e)}
