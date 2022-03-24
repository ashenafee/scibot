import interactions
import os
import json
import requests
from dotenv import load_dotenv
from interactions import Client


CROSSREF = "https://api.crossref.org/works/"

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

cse_button = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="CSE",
    custom_id="cse_button"
)

mla_button = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="MLA",
    custom_id="mla_button"
)

apa_button = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="APA",
    custom_id="apa_button"
)

cite_row = interactions.ActionRow(
    components=[cse_button, mla_button, apa_button],
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


@bot.command(
    name="cite",
    description="Cite an article, given a DOI",
    options=[
        interactions.Option(
            name="doi",
            description="The DOI of the article you would like to cite.",
            type=interactions.OptionType.STRING,
            required=True
        )
    ],
)
async def cite(ctx, doi):
    # TODO: Extract this into a function
    # Add metadata and user ID to the database
    with open("cite.json", "r") as f:
        cite_data = json.load(f)
        cite_data[ctx.author.id._snowflake] = doi
    
    with open("cite.json", "w") as f:
        json.dump(cite_data, f, indent=4)
    
    # Crossref does not provide volume or pages

    embed = interactions.Embed(
        title="Cite an article.",
        description="Please select the type of citation you would like to perform.")
    await ctx.send(embeds=[embed], components=[cite_row], ephemeral=True)

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

@bot.component("cse_button")
async def fcse_button(ctx):
    # Get DOI from database
    with open("cite.json", "r") as f:
        data = json.load(f)
    doi = data[ctx.author.id._snowflake]

    response = requests.get(CROSSREF + doi)

    # Parse metadata into JSON
    metadata = response.json()
    metadata = metadata['message']
    
    title = metadata['title'][0]
    publisher = metadata['publisher']
    publishYear = metadata['published']['date-parts'][0][0]
    journal = metadata['short-container-title'][0]

    authors_list = metadata['author']
    authors = ""
    for author in authors_list:
        authors += author['given'] + " " + author['family'] + ", "
    authors = authors[:-2]

    embed = interactions.Embed(
        title=f"CSE Citation.",
        description=f"Your citation for `{doi}`:",
        fields=[interactions.EmbedField(
            name="Citation",
            value=f"{authors}. {publishYear}. {title}. {journal} **VOL|ISS: PGS**",
            inline=False
        ), interactions.EmbedField(
            name="Required",
            value="> ∙ Volume\n> ∙ Issue\n> ∙ Pages",
            inline=True
        ), interactions.EmbedField(
            name="Access",
            value=f"Find the required fields [here](https://sci-hub.mksa.top/{doi}).",
            inline=True
        )]
    )

    await ctx.send(embeds=[embed], ephemeral=True)

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
print("Sci-Bot is live!")