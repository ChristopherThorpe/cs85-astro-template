# pip install alerce pandas matplotlib
import matplotlib.pyplot as plt
from alerce.core import Alerce

client = Alerce()  # no account or token needed
oid = "45121627560013211"  # Rubin object ID from ALeRCE's docs; find others at https://lsst.alerce.online
det = client.query_detections(oid, survey="lsst", format="pandas")
print(det.columns.tolist())  # every column ALeRCE returns for each Rubin detection

for band, d in det.groupby("band_name"):  # Rubin filters u, g, r, i, z, y
    plt.errorbar(d["mjd"], d["psfFlux"], yerr=d["psfFluxErr"], fmt="o", ms=4, label=band)
plt.axhline(0, color="gray", lw=0.5)
plt.xlabel("MJD (days)")
plt.ylabel("Difference-image flux (nJy)")
plt.title(f"Rubin/LSST object {oid} via ALeRCE")
plt.legend()
plt.savefig("rubin_alerts.png", dpi=150)
