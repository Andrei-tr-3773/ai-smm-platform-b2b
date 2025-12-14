# insert_templates.py
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from bson.objectid import ObjectId

# Load environment variables from .env file
load_dotenv(override=True)

connection_string = os.getenv("CONNECTION_STRING_MONGO")
db_name = connection_string.split('/')[-1]

client = MongoClient(connection_string)
db = client[db_name]
collection = db["content_templates"]

templates = [
    {
        "_id": ObjectId("64b8f3f1f1f1f1f1f1f1f1f1"),
        "name": "Game Features Promotion",
        "liquid_template": """
        <main class="main" style="font-family: 'Museo Sans', 'Helvetica'; max-width: 800px; margin: 20px auto; padding: 20px; background-color: #060606; color: #fff; border-radius: 10px;">
            <div class="block-container">
                <section class="preface">
                    <h1 style="font-size: 2.55rem; font-weight: 300; text-align: center; background-image: linear-gradient(90deg, #0460a9 0%, #b896ff 100%); background-clip: text; -webkit-background-clip: text; color: transparent;">
                        {{Title}}
                    </h1>
                    <p class="title" style="font-weight: bold; font-size: 1.2rem; color: #0460a9; text-align: center;">
                        {{Subtitle}}
                    </p>
                    <div class="grid-container" style="padding: 3rem 0; display: grid; grid-template-columns: repeat(2, 1fr); grid-gap: 4rem; font-size: 1rem;">
                        <div class="grid-item icon icon_magnifier">
                            <p>{{Feature1}}</p>
                        </div>
                        <div class="grid-item icon icon_globe">
                            <p>{{Feature2}}</p>
                        </div>
                        <div class="grid-item icon icon_laptop">
                            <p>{{Feature3}}</p>
                        </div>
                        <div class="grid-item icon icon_chain">
                            <p>{{Feature4}}</p>
                        </div>
                    </div>
                    <div class="center-container" style="padding: 3rem 0; display: flex; align-items: center; justify-content: center;">
                        <div class="emphasized-square" style="max-width: 40rem; text-align: center;">
                            <p>{{OfferMessage}}</p>
                        </div>
                    </div>
                    <div class="stButton" style="text-align: center;">
                        <a href="{{Link}}" target="_blank" style="display: inline-block; padding: 10px 20px; background-color: #023761; color: #060606; text-decoration: none; border-radius: 5px;">{{CallToAction}}</a>
                    </div>
                </section>
            </div>
        </main>
        """,
        "items": [
            {"Type": "Text", "Name": "Title", "MaxLength": 100, "Id": "Title", "IsRequired": True},
            {"Type": "Text", "Name": "Subtitle", "MaxLength": 100, "Id": "Subtitle", "IsRequired": True},
            {"Type": "TextArea", "Name": "Feature 1", "MaxLength": 150, "Id": "Feature1", "IsRequired": True},
            {"Type": "TextArea", "Name": "Feature 2", "MaxLength": 150, "Id": "Feature2", "IsRequired": True},
            {"Type": "TextArea", "Name": "Feature 3", "MaxLength": 150, "Id": "Feature3", "IsRequired": True},
            {"Type": "TextArea", "Name": "Feature 4", "MaxLength": 150, "Id": "Feature4", "IsRequired": True},
            {"Type": "TextArea", "Name": "Offer Message", "MaxLength": 200, "Id": "OfferMessage", "IsRequired": True},
            {"Type": "Text", "Name": "Link", "MaxLength": 200, "Id": "Link", "IsRequired": True},
            {"Type": "Text", "Name": "Call To Action", "MaxLength": 50, "Id": "CallToAction", "IsRequired": True}
        ],
        "example_query": "Promote our new game releases with a 50% discount. Highlight the immersive worlds, global community, seamless gameplay, and team challenges. Include a call to action to shop now."
    },
    {
        "_id": ObjectId("64b8f3f1f1f1f1f1f1f1f1f2"),
        "name": "Simple Campaign",
        "liquid_template": """
        <div style="font-family: 'Arial', sans-serif; max-width: 600px; margin: 20px auto; padding: 20px; border: 1px solid #ccc; border-radius: 10px; background-color: #f9f9f9;">
            <h1 style="color: #333; text-align: center;">{{HeaderText}}</h1>
            <h2 style="color: #555; text-align: center;">{{SubheaderText}}</h2>
            <p style="color: #666; font-size: 14px; line-height: 1.6;">{{BodyText}}</p>
        </div>
        """,
        "items": [
            {"Type": "Text", "Name": "Header Text", "MaxLength": 50, "Id": "HeaderText", "IsRequired": True},
            {"Type": "Text", "Name": "Subheader Text", "MaxLength": 50, "Id": "SubheaderText", "IsRequired": False},
            {"Type": "TextArea", "Name": "Body Text", "MaxLength": 2000, "Id": "BodyText", "IsRequired": True}
        ],
        "example_query": "Announcing a scheduled maintenance on August 12, 2022. Please ensure all work is saved and log out by 10:00 AM UTC to avoid data loss."
    },
    {
        "_id": ObjectId("64b8f3f1f1f1f1f1f1f1f1f3"),
        "name": "Call to Action (with Image)",
        "liquid_template": """
        <div style="font-family: 'Museo Sans', 'Helvetica'; max-width: 600px; margin: 20px auto; padding: 20px; border: 1px solid var(--SNOW); border-radius: 10px; background-color: var(--NIGHT); color: var(--WHITE);">
            <h1 style="color: var(--WHITE); text-align: center;">{{Title}}</h1>
            <p style="color: var(--WHITE); font-size: 1rem; line-height: 1.6; font-weight: 300;">{{Description}}</p>
            <img src="{{ImageURL}}" alt="Social Media Image" style="width: 100%; height: auto; border-radius: 8px; margin: 15px 0;"/>
            <div style="text-align: center;">
                <a href="{{Link}}" target="_blank" style="display: inline-block; padding: 10px 20px; background-color: var(--SEA); color: var(--NIGHT); text-decoration: none; border-radius: 5px;">{{CallToAction}}</a>
            </div>
        </div>
        """,
        "items": [
            {"Type": "Text", "Name": "Title", "MaxLength": 100, "Id": "Title", "IsRequired": True},
            {"Type": "TextArea", "Name": "Description", "MaxLength": 2000, "Id": "Description", "IsRequired": True},
            {"Type": "Text", "Name": "Image URL", "MaxLength": 200, "Id": "ImageURL", "IsRequired": True},
            {"Type": "Text", "Name": "Link", "MaxLength": 200, "Id": "Link", "IsRequired": True},
            {"Type": "Text", "Name": "Call To Action", "MaxLength": 50, "Id": "CallToAction", "IsRequired": True}
        ],
        "example_query": "Launch a captivating marketing campaign to promote the new version of our XYZ game in the Metaverse. Highlight its immersive gameplay, enhanced graphics, and exclusive in-game rewards. Use the following image to captivate your audience: https://images.unsplash.com/photo-1511512578047-dfb367046420?w=800. Emphasize how this new version offers an unparalleled virtual experience that redefines gaming."
    },
    {
        "_id": ObjectId("64b8f3f1f1f1f1f1f1f1f1f4"),
        "name": "Push Notification Preview",
        "liquid_template": """
        <div style="background-color: #fff; border: 1px solid #ccc; border-radius: 8px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); width: 300px; padding: 16px; display: flex; align-items: center;">
            <img src="https://static.vecteezy.com/system/resources/previews/023/986/666/non_2x/line-app-logo-line-app-logo-transparent-line-app-icon-transparent-free-free-png.png" alt="App Icon" style="border-radius: 50%; width: 50px; height: 50px; margin-right: 16px;">
            <div style="flex: 1;">
                <p style="font-size: 16px; font-weight: bold; margin: 0; color: #333;">{{Title}}</p>
                <p style="font-size: 14px; margin: 4px 0 0 0; color: #555;">{{Message}}</p>
                <p style="font-size: 12px; color: #888; margin-top: 8px;">2 mins ago</p>
            </div>
        </div>
        """,
        "items": [
            {"Type": "Text", "Name": "Title", "MaxLength": 100, "Id": "Title", "IsRequired": True},
            {"Type": "TextArea", "Name": "Message", "MaxLength": 200, "Id": "Message", "IsRequired": True}
        ],
        "example_query": "Create a push notification preview for a special offer with a title and message."
    },
    {
        "_id": ObjectId("64b8f3f1f1f1f1f1f1f1f1f5"),
        "name": "Message with Idioms",
        "liquid_template": """
        <div style="font-family: 'Museo Sans', 'Helvetica'; max-width: 40rem; margin: 3rem auto; padding: 3rem; border: 1px solid var(--SNOW); border-radius: 10px; background-color: var(--NIGHT); color: var(--WHITE);">
            <h1 style="color: var(--LILIAC); text-align: center; font-size: 2.55rem; font-weight: 300;">{{Title}}</h1>
            <h2 style="color: var(--SEA); text-align: center; font-size: 2.22rem; font-weight: 300;">{{Subtitle}}</h2>
            <hr style="border: 0; height: 1px; background: var(--SNOW); margin: 20px 0;">
            <p style="color: var(--WHITE); font-size: 1rem; line-height: 1.5; font-weight: 300;">{{Body}}</p>
        </div>
        """,
        "items": [
            {"Type": "Text", "Name": "Title", "MaxLength": 100, "Id": "Title", "IsRequired": True},
            {"Type": "Text", "Name": "Subtitle", "MaxLength": 200, "Id": "Subtitle", "IsRequired": False},
            {"Type": "TextArea", "Name": "Body", "MaxLength": 2000, "Id": "Body", "IsRequired": True}
        ],
        "example_query": "Compose a text to a friend filled with English idioms. Offer life advice in a friendly tone, using idioms to convey wisdom and humor. Try to use as much English-specific idioms as you can"
    },
    {
        "_id": ObjectId("64b8f3f1f1f1f1f1f1f1f1f6"),
        "name": "Header & Body Campaign",
        "liquid_template": """
        <div id="root">
            <div class="preface">
                <div class="center-container">
                    <div class="emphasized-square">
                        <h1><span>{{HeaderText}}</span></h1>
                        <p>{{BodyText}}</p>
                        <img src="https://images.unsplash.com/photo-1538481199705-c710c4e965fc?w=800" alt="Game Screenshot" style="width: 100%; margin-top: 1rem;">
                    </div>
                </div>
            </div>
        </div>
        """,
        "items": [
            {"Type": "Text", "Name": "Header Text", "MaxLength": 50, "Id": "HeaderText", "IsRequired": True},
            {"Type": "TextArea", "Name": "Body Text", "MaxLength": 2000, "Id": "BodyText", "IsRequired": True}
        ],
        "example_query": "New RPG Game Released! Embark on an epic journey in our latest RPG game. Explore vast worlds, engage in thrilling battles, and uncover hidden secrets. Customize your character, forge alliances, and shape your destiny in this immersive adventure."
    }
]

collection.insert_many(templates)
print("Templates inserted successfully!")