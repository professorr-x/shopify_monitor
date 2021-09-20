from django.shortcuts import render
import requests
import json
from datetime import datetime
import time
import random
import sqlite3
from monitor.models import Products

from discord_webhook import DiscordWebhook, DiscordEmbed

def send_webhook(webhook, product_title, price, image_url, desc, handle):
    embed = DiscordEmbed(title=product_title, url="https://funkoeurope.com/products/"+ handle, description=desc, color=242424)
    embed.set_author(
        name="Funko",
        url="https://funkoeurope.com/",
        icon_url="https://cdn.shopify.com/s/files/1/0433/1952/5529/files/Funko_Logo_White_140x@2x.png?v=1602310645",
    )
    #embed.set_footer(text="Embed Footer Text")
    # set thumbnail
    embed.set_thumbnail(url=image_url)
    embed.set_timestamp()
    ## Set `inline=False` for the embed field to occupy the whole line
    embed.add_embed_field(name="Status", value="Available", inline=False)
    embed.add_embed_field(name="Price", value=price, inline=False)

    webhook.add_embed(embed)
    response = webhook.execute()
    if response[0].status_code != 200:
        embed = webhook.get_embeds()

        for i in range(len(embed)):
            webhook.remove_embed(i)
        response = webhook.execute()
        exit()

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

                        new_product = Products(
                                product_id = product_id,
                                title = title,
                                handle = handle,
                                variant_id = variant_id,
                                variant_title = variant_title,
                                available = available,
                                price = price,
                                image_url = image_url
                            )
                        new_product.save()
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

def run_monitor(webhook, watch_list):
    url = "https://funkoeurope.com/products.json?page="

    db = PRODUCTDATABASE()
    
    if Products.objects.first() == None:
        db.set_up_db(url)

    # watch_list = ["6-exodia-the-forbidden-one-yu-gi-oh", "concept-series-snowtrooper-star-wars", "stefon-diggs-nfl-bills"]

    # with open("watch_list.txt", "r") as f:
    #     for line in f:
    #         line = line.replace("\n", "")
    #         watch_list.append(line)

    payload = {}
    headers = {}

    client = requests.Session()

    x = 1

    while True:
        products_url = url + str(x)
        try:
            response = client.get(products_url)
            product_data = response.json()
            product_data = product_data["products"]
            x += 1
            if len(product_data):
                for product in product_data:
                    datetimeObj = datetime.now()

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


                        # insert product into db if it doesnt exist already
                        Products.objects.filter(product_id = product_id).first()
                        if Products.objects.filter(product_id = product_id).first() == None :

                            new_product = Products(
                                product_id = product_id,
                                title = title,
                                handle = handle,
                                variant_id = variant_id,
                                variant_title = variant_title,
                                available = available,
                                price = price,
                                image_url = image_url
                            )
                            new_product.save()
                            send_webhook(webhook, title, price, image_url, "New Product", handle)
                            time.sleep(random.randint(0,30))
                        else:
                            # check if availabilty matches
                            print('availability check')
                            if available != Products.objects.filter(variant_id = variant_id).first().available:
                                p = Products.objects.filter(variant_id = variant_id).first()
                                p.available = available
                                p.save()

                        for handle in watch_list:
                            if handle in product["handle"]:
                                if variant["available"]:
                                    send_webhook(webhook, title, price, image_url, "Product Is Available", handle)
                                    time.sleep(random.randint(0,30))
            else:
                x = 0

        except Exception as e:
            print(e)
            print('Delaying next request')
            time.sleep(random.randint(0,20))


def index(request):
    if request.method == "POST":
        webhook = DiscordWebhook(url=request.POST["webhook_url"], username="Funky Monitor")
        watch_list = request.POST["watch_list"]
        if watch_list:
            watch_list = watch_list.replace("\n","")
            watch_list = watch_list.replace("\r","")
            watch_list = watch_list.split()

        run_monitor(webhook, watch_list)
        return render(
            request,
            "monitor/index.html")
    else:
        return render(
            request,
            "monitor/index.html")