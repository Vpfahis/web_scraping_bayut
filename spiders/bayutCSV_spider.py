import scrapy

class MyBayutSpider(scrapy.Spider):
    name = "bayut_spider"
    allowed_domains = ["www.bayut.com"]
    start_urls = ["https://www.bayut.com/to-rent/property/dubai/"]

    # Add custom settings to export data as CSV
    custom_settings = {
        'FEED_FORMAT': 'csv',  # Export as CSV
        'FEED_URI': 'output.csv',  # Name of the CSV file
        'FEED_EXPORT_FIELDS': ['property_id', 'property_url', 'purpose', 'type', 'added_on', 'furnishing', 
                               'price', 'location', 'bed_bath_size', 'permit_number', 'agent_name', 
                               'primary_image_url', 'breadcrumbs', 'amenities']  # Fields to export
    }

    def parse(self, response):
        # Extract product URLs on the current page
        product_urls = response.css('a.d40f2294::attr(href)').getall()  
        for url in product_urls:
            yield response.follow(url, self.parse)

        # Extract the URL of the next page using the 'a' tag with title="Next"
        next_page = response.css('a[title="Next"]::attr(href)').get()

        # Follow the next page if available
        if next_page is not None:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(next_page_url, callback=self.parse)

        # Extract product details
        price = response.css('span._2d107f6e::text').get().strip()
        primary_image = response.css('img._4a3dac18::attr(src)').get()
        location = response.css('div.e4fd45f0::text').get().strip()
        bed_bath_size = response.css('span._140e6903::text').get().strip()
        description_parts = response.css('span._3547dac9::text').getall()
        description = " ".join([part.strip() for part in description_parts])

        type = ", ".join(response.css('span._2fdf7fc5[aria-label="Type"]::text').getall())
        purpose = ", ".join(response.css('span._2fdf7fc5[aria-label="Purpose"]::text').getall())
        furnishing = ", ".join(response.css('span._2fdf7fc5[aria-label="Furnishing"]::text').getall())
        added_on = ", ".join(response.css('span._2fdf7fc5[aria-label="Reactivated date"]::text').getall())
        property_id = ", ".join(response.css('span._2fdf7fc5[aria-label="Reference"]::text').getall())
        agent = response.css('span._64aa14db a._1264833a::text').getall()

        # Check if the first selector returned any results
        if not agent:  # If agent is empty
            agent = response.css('span._4c376836.undefined a.d2d04ff3::text').getall()

        agent = [name.strip() for name in agent if name.strip()]
        permit_number = response.css('span.e56292b8[aria-label="Permit Number"]::text').getall()
        amenities = response.css('div._1c78af3b + div._117b341a span._7181e5ac::text').getall()
        amenities = [amenity.strip() for amenity in amenities]

        breadcrumbs = response.css('div.e28fea44 a._43ad44d9::text').getall()
        breadcrumbs = [breadcrumb.strip() for breadcrumb in breadcrumbs if breadcrumb.strip()]

        yield {
            'property_id': property_id,
            'property_url': response.url,
            'purpose': purpose,
            'type': type,
            'added_on': added_on,
            'furnishing': furnishing,
            'price': {
                "currency": "AED",
                "amount": price
            },
            'location': location,
            'bed_bath_size': bed_bath_size,
            'permit_number': permit_number,
            'agent_name': agent,
            'primary_image_url': primary_image,
            'breadcrumbs': breadcrumbs,
            'amenities': amenities
        }
