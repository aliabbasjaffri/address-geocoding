import os
import googlemaps
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv


env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)

API_KEY = os.environ.get("API_KEY")


class GeocodeAddresses:
    def __init__(self) -> None:
        self.gmaps = googlemaps.Client(key=API_KEY)

    def _geocode_address(self, address: str) -> dict:
        geocode_result = self.gmaps.geocode(
            address, components={"locality": "München", "country": "DE"}
        )

        # print(geocode_result)
        # print(geocode_result[0]["formatted_address"])

        return geocode_result[0]["geometry"]["location"]

    def _find_location(self, address: str, city: str) -> dict:
        geocode_result = self.gmaps.find_place(
            address, "textquery", location_bias=f"circle:500@{city}"
        )
        place_id = geocode_result["candidates"][0]["place_id"]

        # Retrieve place details
        place_details = self.gmaps.place(
            place_id,
            # fields=["formatted_address", "geometry/location", "website", "review"],
            fields=["formatted_address", "geometry/location", "website"],
        )
        print(place_details)

        return place_details

    def geocode_all_addresses(self) -> None:
        try:
            # addresses.csv contains list of cafe addresses, with name
            df = pd.read_csv("addresses.csv", header=None)

            # rename columns
            df.columns = ["Name", "Address", "Postcode", "City"]

            print(df.tail(n=5))

            # general cleanup for any whitespace
            df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

            # combine column values with a space in between them
            for index, row in df.iterrows():
                if row.isna().any():
                    complete_address = self._find_location(
                        address=row["Name"], city=row["City"]
                    )
                    df.at[index, "Address"] = complete_address["result"][
                        "formatted_address"
                    ]
                    df.at[index, "Postcode"] = int(
                        complete_address["result"]["formatted_address"]
                        .split(",")[-2]
                        .strip()
                        .split(" ")[0]
                    )
                    point = complete_address["result"]["geometry"]["location"]

                else:
                    address = (
                        row["Name"] + " " + row["Address"] + " " + str(row["Postcode"])
                    )
                    point = self._geocode_address(address=address)
                    row["Postcode"] = int(row["Postcode"])

                df.at[index, "lat"] = point["lat"]
                df.at[index, "lon"] = point["lng"]

                print(f"Geocoded address: {row['Name']}")

            df.to_json("data.json", orient="records", force_ascii=False)
        except Exception as e:
            print(f"Exception occurred: {e}")


if __name__ == "__main__":
    geocode = GeocodeAddresses()
    geocode.geocode_all_addresses()
    # geocode._find_location(address="Cafe DaMe")
