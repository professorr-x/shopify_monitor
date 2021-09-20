from discord_webhook import DiscordWebhook, DiscordEmbed
import time

webhook = DiscordWebhook(url="https://discord.com/api/webhooks/616238003186171904/vZQsfbDT9jifuIejEBUR6zqOhToDylWsKt5CScqN8FQJaEzT9EoW1DQgEWeryPJrlv2M", username="Funky Monitor")

def send_webhook(product_title, price, image_url, desc, handle):
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




    
