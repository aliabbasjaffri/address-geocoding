import os
import json
import urllib
import requests
import pandas as pd
from geopy.geocoders import Nominatim

base_url = "https://maps.googleapis.com/maps/api/geocode/json?"
ADDRESS = "Heiliggeiststraße 1, 80331 München"

def google_maps_geocode_address() -> None:
    parameters = {
        "address": ADDRESS,
        "key": str(os.environ["AUTH_KEY"])
    }
    
    print(f"{base_url}{urllib.parse.urlencode(parameters)}")
    r = requests.get(f"{base_url}{urllib.parse.urlencode(parameters)}")
    data = json.loads(r.content)
    print(data)

    # get location cordinates; lat and long
    print(data.get("results")[0].get("geometry").get("location"))


def geopy_geocode_address() -> None:
    # https://geopy.readthedocs.io/en/stable/
    
    geolocator = Nominatim(user_agent="cafe_around_the_corner")
    data = geolocator.geocode(ADDRESS)

    # check latitude, longitude
    print(f"{data.raw.get('lat')}, {data.raw.get('lon')}")
    
    # validation check
    print(geolocator.reverse(f"{data.raw.get('lat')}, {data.raw.get('lon')}"))

def geopy_get_bulk_locations() -> None:
    try:
        geolocator = Nominatim(user_agent="cafe_around_the_corner")

        # addresses.csv contains list of cafe addresses, with name
        df = pd.read_csv("addresses.csv")
        
        # general cleanup for any whitespace
        df.rename(columns=lambda x: x.strip(), inplace=True)
        df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

        # applying geocode for all addresses
        df["loc"] = df["Address"].apply(geolocator.geocode)
        df["point"]= df["loc"].apply(lambda loc: tuple(loc.point) if loc else None)

        # creating columns for latitude, longitude and altitude
        df[['lat', 'lon', 'altitude']] = pd.DataFrame(df['point'].to_list(), index=df.index)
        
        # saving information to a csv
        df.to_csv("addresses_formatted.csv", index=False, encoding="utf-8")
    except Exception as e:
        print(f"Exception occurred: {e}")

def clean_addresses() -> None:
    df = pd.read_csv("addresses_formatted.csv")

    # getting rid of unnecessary columns
    df.drop(columns=["loc", "point", "altitude"], inplace=True)
    
    # extracting postcode from the address
    df["PostCode"] = df["Address"].apply(lambda x: x.split(" ")[-2])
    
    # sorting addresses as per postcode
    df.sort_values("PostCode", inplace=True)
    print(df.to_dict("records"))
    
    # writing all the sorted addresses to json
    df.to_json("data.json", orient="records", lines=True)

    df.to_csv("final_addresses.csv", index=False, encoding="utf-8")


if __name__ == "__main__":
    # google_maps_geocode_address()
    # geopy_geocode_address()
    # geopy_get_bulk_locations()
    clean_addresses()
