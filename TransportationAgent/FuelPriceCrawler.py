import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, DefaultMarkdownGenerator

async def fetch_fuel_prices(city: str) -> str:
    """Fetches fuel prices for a certain Turkish city as markdown.

    Args:
        city: Name of the Turkish city. Must be in lowercase using only English alphabet characters. For example, 'ankara', 'istanbul', 'izmir', "karabuk", "agri". Convert Turkish characters (e.g., 'ğ', 'ş', 'ç', 'ü', 'ı', 'ö') to their English equivalents ('g', 's', 'c', 'u', 'i', 'o').

    Returns:
        Markdown of fuel prices of the chosen Turkish city.
    """

    md_generator = DefaultMarkdownGenerator(
        options={"ignore_images": True}
    )

    config = CrawlerRunConfig(
        target_elements=[
            'h1.page-title', # Descriptive title
            'div.table.sortable',  # Fuel prices table
            'div.article-content.kur-page > span'  # Summary text
        ],
        markdown_generator=md_generator
    )

    async with AsyncWebCrawler() as crawler:

        if city.replace("İ", "i").casefold() == "istanbul":
            ist_europe = await crawler.arun("https://www.doviz.com/akaryakit-fiyatlari/istanbul-avrupa", config=config)
            ist_asia = await crawler.arun("https://www.doviz.com/akaryakit-fiyatlari/istanbul-anadolu", config=config)
            return ist_europe.markdown + ist_asia.markdown
        else:
            url = f"https://www.doviz.com/akaryakit-fiyatlari/{city}"
            result = await crawler.arun(url, config=config)
            return result.markdown



# To run it (e.g., for Karabuk):
async def main():
    markdown = await fetch_fuel_prices("istanbul")
    print(markdown)

if __name__ == "__main__":
    asyncio.run(main())
