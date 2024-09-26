####### FOR CSV #########
import scrapy
import csv
from scrapy.exceptions import CloseSpider

class MyBayutSpider(scrapy.Spider):
    name = "my_bayut_spider"
    allowed_domains = ["www.bayut.com"]
    start_urls = ["https://www.bayut.com/to-rent/property/dubai/"]

    def __init__(self, *args, **kwargs):
        """
        Initialize the spider and open the CSV file for writing.
        """
        super(MyBayutSpider, self).__init__(*args, **kwargs)
        self.output_file = 'bayut_properties.csv'

        # Open the CSV file for writing
        self.csv_file = open(self.output_file, 'w', newline='', encoding='utf-8')
        self.csv_writer = csv.writer(self.csv_file)

        # Write the header row on the left side
        self.csv_writer.writerow(['Field Name', 'Property 1', 'Property 2', 'Property 3', '...'])

        # Initialize a counter for the number of crawled properties
        self.property_count = 0

        # Set the maximum number of properties to extract
        self.max_properties = 1500

    def parse(self, response):
        # Extract product URLs on the current page
        product_urls = response.css('a.d40f2294::attr(href)').getall()  
        for url in product_urls:
            # Stop crawling if the limit is reached
            if self.property_count >= self.max_properties:
                raise CloseSpider(reason="Reached 1500 properties")
            yield response.follow(url, self.parse_property_details)

        # Extract the URL of the next page using the 'a' tag with title="Next"
        next_page = response.css('a[title="Next"]::attr(href)').get()

        # Follow the next page if available and the limit hasn't been reached
        if next_page is not None and self.property_count < self.max_properties:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(next_page_url, callback=self.parse)

    def parse_property_details(self, response):
        """
        Parse individual property pages to extract property details.
        """
        # Extract property details
        price = response.css('span._2d107f6e::text').get().strip() if response.css('span._2d107f6e::text') else 'N/A'
        primary_image = response.css('img._4a3dac18::attr(src)').get() if response.css('img._4a3dac18::attr(src)') else 'N/A'
        location = response.css('div.e4fd45f0::text').get().strip() if response.css('div.e4fd45f0::text') else 'N/A'
        bed_bath_size = response.css('span._140e6903::text').get().strip() if response.css('span._140e6903::text') else 'N/A'
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

        # Organize property details in dictionary
        property_details = {
            'Property ID': property_id,
            'Property URL': response.url,
            'Purpose': purpose,
            'Type': type,
            'Added On': added_on,
            'Furnishing': furnishing,
            'Price': price,
            'Location': location,
            'Bed/Bath/Size': bed_bath_size,
            'Permit Number': permit_number,
            'Agent Name': agent,
            'Primary Image URL': primary_image,
            'Breadcrumbs': breadcrumbs,
            'Amenities': amenities
        }

        # Write each property field in column format (column title on the left side)
        for field_name, field_value in property_details.items():
            # Ensure field_value is a string before writing to CSV
            if isinstance(field_value, list):
                field_value = ", ".join(field_value)
            self.csv_writer.writerow([field_name, field_value])

        # Increment the property counter
        self.property_count += 1

        # Stop the spider once the property limit is reached
        if self.property_count >= self.max_properties:
            raise CloseSpider(reason="Reached 1500 properties")

    def close(self, reason):
        """
        Close the CSV file when the spider is finished.
        """
        self.csv_file.close()
