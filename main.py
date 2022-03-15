import interactions
import os
from dotenv import load_dotenv
from interactions import Client


load_dotenv()
bot = Client(token=os.getenv("DISCORD_BOT_TOKEN"))

search_doi = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="DOI",
    custom_id="search_doi"
)

search_pmid = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="PMID",
    custom_id="search_pmid"
)

search_url = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="URL",
    custom_id="search_url"
)

search_options = interactions.ActionRow(
    components=[search_doi, search_pmid, search_url],
)

back_button = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Back",
    custom_id="back_button"
)

search_button = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Search",
    custom_id="search_button"
)

search_row = interactions.ActionRow(
    components=[back_button, search_button],
)

######### COMMANDS ############

@bot.command(
    name="search",
    description="Search for an article on sci-hub.",
)
async def search(ctx):
    embed = interactions.Embed(
        title="Search for an article on sci-hub.",
        description="Please select the type of search you would like to perform.")
    await ctx.send(embeds=[embed], components=[search_options], ephemeral=True)

######## COMPONENTS ###########

@bot.component("back_button")
async def fback_button(ctx):
    embed = interactions.Embed(
        title="Search for an article on sci-hub.",
        description="Please select the type of search you would like to perform.")
    await ctx.edit(embeds=[embed], components=[search_options])

@bot.component("search_button")
async def fsearch_button(ctx):
    title = ""
    if ("DOI" in ctx.message.embeds[0].description):
        title = "DOI"
    elif ("PMID" in ctx.message.embeds[0].description):
        title = "PMID"
    else:
        title = "URL"

    search_input = interactions.TextInput(
        style=interactions.TextStyleType.SHORT,
        label=f"Input the article's {title}.",
        custom_id="search_input"
    )

    modal = interactions.Modal(
        title=f"Sci-Hub Search",
        custom_id="search_modal",
        components=[search_input]
    )
    await ctx.popup(modal)

@bot.component("search_doi")
async def fsearch_doi(ctx):
    embed = interactions.Embed(
        title="Sci-Hub DOI Lookup.",
        description="Please enter the DOI of the article you would like to search for."
    )
    await ctx.edit(embeds=[embed], components=[search_row])

@bot.component("search_pmid")
async def fsearch_pmid(ctx):
    embed = interactions.Embed(
        title="Sci-Hub PMID Lookup.",
        description="Please enter the PMID of the article you would like to search for."
    )
    await ctx.edit(embeds=[embed], components=[search_row])

@bot.component("search_url")
async def fsearch_url(ctx):
    embed = interactions.Embed(
        title="Sci-Hub URL Lookup.",
        description="Please enter the URL of the article you would like to search for."
    )
    await ctx.edit(embeds=[embed], components=[search_row])

########### MODALS ############

@bot.modal("search_modal")
async def fsearch_modal(ctx, response: str):
    if (response == ""):
        await ctx.send("Please input a search term.", ephemeral=True)
        return

    embed = interactions.Embed(
        title="Sci-Hub Results",
        description=f"You can access your article [here](https://sci-hub.mksa.top/{response})."
    )

    await ctx.send(embeds=[embed], ephemeral=True)

bot.start()