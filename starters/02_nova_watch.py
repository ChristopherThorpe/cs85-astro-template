# pip install requests pandas matplotlib
# Needs a FREE AAVSO account: sign up at https://apps.aavso.org/v2/accounts/signup/ , copy the API token
# from your account settings page, then in Terminal run:  export AAVSO_TOKEN="paste-your-token"
import os, time, requests, pandas as pd, matplotlib.pyplot as plt

star, since = "T CrB", "2025-01-01"  # or: star, since = "V1452 Tau", "2026-08-01"
url = "https://apps.aavso.org/v2/api/observations/photometry/"  # docs: https://docs.aavso.org/observations
headers = {"Authorization": "Token " + os.environ["AAVSO_TOKEN"]}
rows = []
for page in range(1, 21):  # AAVSO asks for at most 1 request every 10 s
    r = requests.get(url, headers=headers, params={"target": star, "band": 2, "start_date": since, "page": page}, timeout=60)
    r.raise_for_status()  # stops with a clear error if the token or URL is wrong
    rows += r.json()["results"]
    if not r.json()["next"]: break  # no more pages
    time.sleep(10)
df = pd.DataFrame(rows)  # band 2 = Johnson V
dates = pd.to_datetime(df["jd_dbl"] - 2440587.5, unit="D")  # Julian Date -> calendar date
plt.scatter(dates, pd.to_numeric(df["magnitude"], errors="coerce"), s=4)
plt.gca().invert_yaxis()  # brighter = up
plt.ylabel("V magnitude"); plt.title(f"{star}: AAVSO V-band observations")
plt.savefig("nova_watch.png", dpi=150)
