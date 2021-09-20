import sqlite3
import requests
import json

class PRODUCTDATABASE:
    con = sqlite3.connect('pop.db')
    cur = con.cursor()

    def create_table(self, url):
        try:
            self.cur.execute('''create table if not exists products
               (product_id text, title text, handle text, variant_id text, variant_title text, available numeric, price REAL, image_url text)''')
            
            self.cur.execute("SELECT * FROM products")
            result = self.cur.fetchone()

            if result == None:
                ### THIS IS EXECUTED ON ALL RUNS
                self.set_up_db(url)
        except Exception as e:
            print(e)

    def set_up_db(self, url):
        print("Setting up database")
        x =0
        
        while True:
            products_url = url + str(x)
            x+= 1
            try:
                response = requests.get(products_url)
                product_data = response.json()
                product_data = product_data["products"]
                if len(product_data):
                    for product in product_data:
                        for variant in product["variants"]:
                            product_id = product["id"]
                        title = product["title"].replace("'","")
                        handle = product["handle"]
                        variant_id = variant["id"]
                        variant_title = variant["title"]
                        available = variant["available"]
                        price = variant["price"]
                        for image in product["images"]:
                            image_url = image["src"]

                        self.insert_record(
                            product_id,
                                title,
                                handle,
                                variant_id,
                                variant_title,
                                available,
                                price,
                                image_url
                        )
                else:
                    break
            except Exception as e:
                print(e)



    def check_record_exists(self, variant_id):
        try:
            self.cur.execute("SELECT * FROM products WHERE variant_id = {}".format(variant_id))
            if self.cur.fetchall():
                return True
            else:
                return False
        except Exception as e:
            print(e)
            return False
    
    def check_record_availability(self, variant_id):
        try:
            self.cur.execute("SELECT * FROM products WHERE variant_id = {}".format(variant_id))
            result = self.cur.fetchone()
            return result[5]
        except Exception as e:
            print(e)
            return None

    def update_record(self, variant_id, available):
        try:
            self.cur.execute("UPDATE products SET available={} WHERE variant_id = {}".format(available, variant_id))
        except Exception as e:
            print(e)

    def insert_record(self, product_id, title, handle, variant_id, variant_title, available, price, image_url):
        try:
            self.cur.execute("INSERT INTO products VALUES ('{}', '{}','{}', '{}','{}', '{}','{}', '{}')".format(product_id, title, handle, variant_id, variant_title, available, price, image_url))
            print('Product added successfully to database ')
            self.con.commit()
        except Exception as e:
            print(e)
