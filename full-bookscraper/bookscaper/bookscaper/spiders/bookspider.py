import scrapy
from bookscaper.items import BookItem

class BookspiderSpider(scrapy.Spider):
    name = "bookspider"
    allowed_domains = ["books.toscrape.com"]  #prevents our spider to srape the other websites/pages
    start_urls = ["https://books.toscrape.com/"] # first url that spider to start scaping

    custom_settings = {
        'FEEDS' : {
            'booksdata.json' : {'format':'json' , 'overwrite' : True}
        }
    }
    
    def parse(self,response):
        
        #first we take all the product(in this case it's books) with response css   
        books = response.css('article.product_pod').get()
        for book in books:
            relative_url =  response.css('h3 a ::attr(href)').get() # getting every book's relative url 
            if 'catalogue/' in relative_url:
                book_url = 'https://books.toscrape.com/' + relative_url
            else :
                book_url = 'https://books.toscrape.com/catalogue/' + relative_url
            
            yield response.follow(book_url, callback = self.parse_book_page) # we are calling a func that parsing book's features

        #for crawling in site pages(not only books) 
        next_page = response.css('li.next a::attr(href)').get()   
        if next_page is not None:
            if 'catalogue/' in next_page:
                next_page_url = 'https://books.toscrape.com/' + next_page
            else:
                next_page_url = 'https://books.toscrape.com/catalogue/' + next_page
            yield response.follow(next_page_url, callback=self.parse)


    def parse_book_page(self,response):
        table_rows = response.css('table tr')
        book_item = BookItem()
        
        book_item['url'] = response.url,
        book_item['title'] = response.css('.product_main h1::text').get(),
        book_item['upc'] = table_rows[0].css("td ::text").get(),
        book_item['product_type' ] = table_rows[1].css("td ::text").get(),
        book_item['price_excl_tax'] = table_rows[2].css("td ::text").get(),
        book_item['price_incl_tax'] = table_rows[3].css("td ::text").get(),
        book_item['tax'] = table_rows[4].css("td ::text").get(),
        book_item['availability'] = table_rows[5].css("td ::text").get(),
        book_item['num_reviews']=  table_rows[6].css("td ::text").get(),
        book_item['stars'] = response.css("p.star-rating").attrib['class'],
        book_item['category'] = response.xpath("//ul[@class='breadcrumb']/li[@class='active']/preceding-sibling::li[1]/a/text()").get(),
        book_item['description'] = response.xpath("//div[@id='product_description']/following-sibling::p/text()").get(),
        book_item['price'] = response.css('p.price_color ::text').get(),
        
        yield book_item      

        #We are taking the values as tuples to remain the consistency and correctness of the scraped values.
        #In Python, when you put a trailing comma after a single value, it creates a tuple with that single value. This is known as a singleton tuple.
        # book_item['url'] = response.url, For example, response.url, is a tuple with a single element, which is response.url. Similarly, other lines create singleton tuples for each field.
        # When you yield the book_item, which contains these singleton tuples, Scrapy might be treating it differently during the item export process. 
        # The default Scrapy behavior is to export items as dictionaries, but the behavior can vary based on the item exporter


# WRITING XPATHS
#response.xpath("//ul[@class='breadcrumb']/li[@class='active']/preceding-sibling::li[1]/a/text()").get() -- preceding-sibling ile içine girdiğimiz active classının en iç katmanından dışarı doğru gidebiliriz
#response.xpath("//div[@id='product_description']/following-sibling::p/text()").get()



