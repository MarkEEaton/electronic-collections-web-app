import httpx
import json
import math
import os
from dotenv import load_dotenv
from pprint import pprint

load_dotenv()

apikey = os.getenv("NZ_API_KEY")
url1 = "https://api-na.hosted.exlibrisgroup.com/almaws/v1/electronic/e-collections?limit=100&offset={}&format=json&apikey={}"
url2 = "https://api-na.hosted.exlibrisgroup.com/almaws/v1/electronic/e-collections/{}?apikey={}&format=json"

def sub_fetch(id_number):
    """ get e-collection level data """
    sub_data = httpx.get(url2.format(id_number, apikey), timeout=500)
    sub_json = sub_data.json()

    # see if there are groups
    try:
        group_data = sub_json["group_setting"]
        groups = []
        for group in group_data:
            groups.append(group["group"]["desc"])
        return [sub_json["activation_date"], groups]

    # if there are no groups or activation date
    except KeyError:
        pass

    # if there are no groups, but there is an activation date
    try:
        return [sub_json["activation_date"], False]

    # if there is no activation date
    except KeyError:
        print(sub_json["public_name"])
        return [False]


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
        if sub_return[0]:
            names.append((x["public_name"], x["id"], sub_return[1]))

# sort alphabetically, case-insensitive
sorted_names = sorted(names, key=lambda x: x[0].casefold())


with open("data.json", "w") as f:
    json.dump(sorted_names, f)
