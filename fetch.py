import httpx
import json
import math
import os
from dotenv import load_dotenv

load_dotenv()

apikey = os.getenv("NZ_API_KEY")
url1 = "https://api-na.hosted.exlibrisgroup.com/almaws/v1/electronic/e-collections?limit=100&offset={}&format=json&apikey={}"
url2 = "https://api-na.hosted.exlibrisgroup.com/almaws/v1/electronic/e-collections/{}?apikey={}&format=json"


def sub_fetch(id_number):
    """get e-collection level data"""
    sub_data = httpx.get(url2.format(id_number, apikey), timeout=500)
    sub_json = sub_data.json()
    return [
        sub_fetch_groups(sub_json),
        sub_fetch_interface(sub_json),
        sub_fetch_vendors(sub_json),
    ]


def sub_fetch_groups(sub_json):
    """get groups data"""
    try:
        group_data = sub_json["group_setting"]
        groups = []
        for group in group_data:
            groups.append(group["group"]["desc"])
        return groups
    except KeyError:
        return False


def sub_fetch_interface(sub_json):
    """get interface data"""
    try:
        return sub_json["interface"]["name"]
    except KeyError:
        return False


def sub_fetch_vendors(sub_json):
    """get vendors data"""
    try:
        return sub_json["interface"]["vendor"]["value"]
    except KeyError:
        return False


offset = 0
data = httpx.get(url1.format(offset, apikey), timeout=500)
json_data = data.json()

# calculate the number of pages of results
pages = math.ceil(json_data["total_record_count"] / 100)

names = []

# paginate
for page in range(pages):
    offset = page * 100
    page_data = httpx.get(url1.format(offset, apikey), timeout=500)
    page_json = page_data.json()

    for x in page_json["electronic_collection"]:

        # function to run collection-level api call
        sub_return = sub_fetch(x["id"])
        names.append(
            (x["public_name"], x["id"], sub_return[0], sub_return[1], sub_return[2])
        )

# sort alphabetically, case-insensitive
sorted_names = sorted(names, key=lambda x: x[0].casefold())


with open("static/data.json", "w") as f:
    json.dump(sorted_names, f)
