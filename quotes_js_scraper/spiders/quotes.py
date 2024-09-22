import scrapy
from quotes_js_scraper.items import QuoteItem
from scrapy_playwright.page import PageMethod


class QuotesSpider(scrapy.Spider):
    name = "quotes"
    allowed_domains = ["quotes.toscrape.com"]

    def start_requests(self):
        url = "https://quotes.toscrape.com/js/"
        yield scrapy.Request(
            url,
            meta=dict(
                playwright=True,
                playwright_include_page=True,
                playwright_page_methods=[PageMethod("wait_for_selector", "div.quote")],
            ),
            errback=self.errback,
        )

    def parse(self, response):
        for quote in response.css("div.quote"):
            quote_item = QuoteItem()
            quote_item["text"] = quote.css("span.text::text").get()
            quote_item["author"] = quote.css("small.author::text").get()
            quote_item["tags"] = quote.css("div.tags a.tag::text").getall()
            self.logger.info(f"Quote: {quote_item}")
            yield quote_item  # Corrected line

        self.log("Saved all quotes")

    async def errback(self, failure):
        self.logger.error(f"Failed to load page: {failure}")
        page = failure.request.meta["playwright_page"]
        await page.close()
