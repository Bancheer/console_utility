import aiohttp
import asyncio
import argparse
from datetime import datetime, timedelta


class ExchangeRateFetcher:
    def __init__(self):
        self.api_url = "https://api.privatbank.ua/p24api/exchange_rates?json&date="

    async def fetch_exchange_rate(self, date):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.api_url}{date}") as response:
                data = await response.json()
                return data

    async def get_exchange_rates(self, days):
        current_date = datetime.now()
        exchange_rates = []

        for _ in range(days):
            formatted_date = current_date.strftime("%d.%m.%Y")
            data = await self.fetch_exchange_rate(formatted_date)

            if 'exchangeRate' in data and data['exchangeRate']:
                eur_data = next((rate for rate in data['exchangeRate'] if rate.get('currency') == 'EUR'), None)
                usd_data = next((rate for rate in data['exchangeRate'] if rate.get('currency') == 'USD'), None)

                if eur_data and usd_data:
                    rates = {
                        formatted_date: {
                            'EUR': {
                                'sale': eur_data.get('saleRate', 0),
                                'purchase': eur_data.get('purchaseRate', 0)
                            },
                            'USD': {
                                'sale': usd_data.get('saleRate', 0),
                                'purchase': usd_data.get('purchaseRate', 0)
                            }
                        }
                    }
                    exchange_rates.append(rates)

            current_date -= timedelta(days=1)

        return exchange_rates


async def main():
    parser = argparse.ArgumentParser(description='Fetch exchange rates for EUR and USD from PrivatBank API.')
    parser.add_argument('days', type=int, help='Number of days to fetch exchange rates for (up to 10 days).')

    args = parser.parse_args()
    days = min(args.days, 10)

    exchange_rate_fetcher = ExchangeRateFetcher()
    exchange_rates = await exchange_rate_fetcher.get_exchange_rates(days)

    print(exchange_rates)

if __name__ == "__main__":
    asyncio.run(main())