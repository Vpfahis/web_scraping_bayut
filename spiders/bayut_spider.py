import scrapy

class MyBayutSpider(scrapy.Spider):
    name = "bayut_spider"
    allowed_domains = ["www.bayut.com"]
    start_urls = ["https://www.bayut.com/to-rent/property/dubai/"]

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


        # Extract product name on the current page
        price = response.css('span._2d107f6e::text').get().strip()

        # yield {
        #     'price': price,
            
        # }

        primary_image = response.css('img._4a3dac18::attr(src)').get()
        
        # yield{
        #     'primary_image' : primary_image,
        # }

        location = response.css('div.e4fd45f0::text').get().strip()

        # yield{
        #     'location' : location,
        # }

        bed_bath_size = response.css('span._140e6903::text').get().strip()

        # yield{
        #     'bed_bath_size' : bed_bath_size,
        # }

        description_parts = response.css('span._3547dac9::text').getall()  # Get all text parts split by <br>
        description = " ".join([part.strip() for part in description_parts]) 

        type = ", ".join(response.css('span._2fdf7fc5[aria-label="Type"]::text').getall())
        purpose = ", ".join(response.css('span._2fdf7fc5[aria-label="Purpose"]::text').getall())
        furnishing = ", ".join(response.css('span._2fdf7fc5[aria-label="Furnishing"]::text').getall())
        added_on = ", ".join(response.css('span._2fdf7fc5[aria-label="Reactivated date"]::text').getall())
        property_id = ", ".join(response.css('span._2fdf7fc5[aria-label="Reference"]::text').getall())


        agent = response.css('span._64aa14db a._1264833a::text').getall()

        # Check if the first selector returned any results
        if not agent:  # If agent is empty
            # Try the second selector
            agent = response.css('span._4c376836 undefined a.d2d04ff3::text').getall()

        # Clean up the agent names, if any
        agent = [name.strip() for name in agent if name.strip()]

        permit_number = response.css('span.e56292b8[aria-label="Permit Number"]::text').getall()

        amenities = response.css('div._1c78af3b + div._117b341a span._7181e5ac::text').getall()
        amenities = [amenity.strip() for amenity in amenities]

        breadcrumbs = response.css('div.e28fea44 a._43ad44d9::text').getall()
        breadcrumbs = [breadcrumb.strip() for breadcrumb in breadcrumbs if breadcrumb.strip()]  # Clean up





        # yield{
        #     'description' : description,
        # }
        yield {
            # 'product_url' : product_urls,
            'price': price,
            'primary_image': primary_image,
            'location': location,
            'bed_bath_size': bed_bath_size,
            'description': description,
            'type' : type,
            'purpose': purpose,
            'furnishing': furnishing,
            'added_on': added_on,
            'property_id': property_id,
            'agent' : agent,
            'permit_number' : permit_number,
            'amenities' : amenities,
            'breadcrumbs' : breadcrumbs
        }
        
        # next_page = response.css('a[title="Next"]::attr(href)').get()

        # # Follow the next page if available
        # if next_page is not None:
        #     next_page_url = response.urljoin(next_page)  # Ensure the full URL is built
        #     yield scrapy.Request(next_page_url, callback=self.parse)