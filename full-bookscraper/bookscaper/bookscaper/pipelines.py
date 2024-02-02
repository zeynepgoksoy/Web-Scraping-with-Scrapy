# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class BookscaperPipeline:
    def process_item(self, item, spider):
        
        #DATA CLEANING AND STRUCTURING 
        adapter = ItemAdapter(item)
        
        # stripping all whitespaces from strings except description
        field_names = adapter.field_names()
        for field_name in field_names:
            if field_name != 'description':
                value = adapter.get(field_name)
                adapter[field_name] = value[0].strip()
                #print('*****',value[0],value[1],'******')

        # switchs category & product type to lowercase
        lowercase_keys = ['category','product_type']
        for lowercase_key in lowercase_keys:
            value = adapter.get(lowercase_key)
            adapter[lowercase_key] = value.lower()

        # converting price to float data type
        price_keys = ['price','price_excl_tax','price_incl_tax','tax']
        for price_key in price_keys:
            value = adapter.get(price_key)
            value = value.replace('£','')
            adapter[price_key] = float(value)
        
        # extracting the number of books in stock from availability
        # "availability": "In stock (19 available)"
        availability_string = adapter.get('availability')
        split_string_array = availability_string.split('(')
        if len(split_string_array) < 2:
            adapter['availability'] =0
        else:
            availability_array = split_string_array[1].split(' ')
            value = availability_array[0]
            adapter['availability'] =int(value)

        
        # reviews --> converting string to number
        num_reviews_string = adapter.get('num_reviews')
        adapter['num_reviews'] = int(num_reviews_string)


        # stars --> converting str to num
        stars_string = adapter.get('stars')
        split_stars_array = stars_string.split(' ')
        stars_text_value = split_stars_array[1]

        if stars_text_value == 'zero':
            adapter['stars'] = 0
        elif stars_text_value == 'one':
            adapter['stars'] = 1
        elif stars_text_value == 'two':
            adapter['stars'] = 2
        elif stars_text_value =='three':
            adapter['stars']  = 3
        elif stars_text_value == 'four':
            adapter['stars'] = 4
        elif stars_text_value == 'five':
            adapter['stars']=5

        return item


import mysql.connector

class SaveToMySQLPipeline:

    def __init__(self):
        self.conn = mysql.connector.connect(
            host = 'localhost',
            user = 'root',
            password = '', #add your password if you have one set
            database = 'books' 
        )

        #Creating cursor, used to execute commands
        self.cur = self.conn.cursor()

        #Creating books table if none exist
        self.cur.execute("""
        CREATE TABLE IF NOT EXIST books(
            id int NOT NULL auto_increment,
            url VARCHAR(255),
            title text,
            upc VARCHAR(255),
            product_type VARCHAR(255),
            price_excl_tax DECIMAL,
            price_incl_tax DECIMAL,
            tax DECIMAL,
            price DECIMAL,
            availabilty INTEGER,
            num_reviews INTEGER,
            stars INTEGER,
            category VARCHAR(255),
            description text,
            PRIMARY KEY(id)
        )
        """)
    def process_item(self, item, spider):

        #Define insert statement
        self.cur.execute("""insert into books(
            url,
            title,
            upc,
            product_type,
            price_exl_tax,
            price_incl_tax,
            tax ,
            price ,
            availabilty ,
            num_reviews ,
            stars ,
            category,
            description 
            ) values(
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
                )""",(
            item["url"],
            item["title"],
            item["upc"],
            item["product_type"],
            item["price_excl_tax"],
            item["price_incl_tax"],
            item["tax"],
            item["price"],
            item["availability"],
            item["num_reviews"],
            item["stars"],
            item["category"],
            str(item["description"][0])
            ))

            #Executing insert of data into databases
            self.conn.commit()
            return item
    
    def close_spider(self,spider):
        
        #Closing cursor and connection to db
        self.cur.close()
        self.conn.close()
