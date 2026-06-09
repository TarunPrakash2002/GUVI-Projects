import os
import requests

folder = "/Users/taruntp7/Documents/GUVI/Telangana PDS Analytics/Datasets/Card Status"
os.makedirs(folder, exist_ok=True)
base = "https://data.telangana.gov.in/sites/default/files/uploaded_resources/fpshop-card-status_{}_{}.csv"

for year in [2023,2024,2025]:
    max_month = 12
    if year == 2025:
        max_month = 5 # this is because the website has datasets only till this month

    for month in range(1,max_month+1):
        url = base.format(month,year)
        filename = f"{folder}/card_{year}_{month:02d}.csv"
        r = requests.get(url)

        if r.status_code == 200: # this is to check if website actually gives a file to download, and only then we download. 
            # This is to avoid downloading error pages instead of actual datasets
            with open(filename,"wb") as f:
                f.write(r.content)
            print("Downloaded:",filename)

        else:
            print("Missing:",url)