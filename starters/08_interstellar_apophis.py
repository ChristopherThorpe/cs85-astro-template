# pip install astroquery matplotlib
from astroquery.jplhorizons import Horizons
import matplotlib.pyplot as plt

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5))
year = {'start': '2025-06-01', 'stop': '2026-06-01', 'step': '2d'}
# Left: 3I/ATLAS (= comet C/2025 N1) vs Earth (399) and Mars (499), Sun-centred, ecliptic plane
for label, hid, idtype in [('3I/ATLAS', 'C/2025 N1', 'designation'), ('Earth', '399', None), ('Mars', '499', None)]:
    v = Horizons(id=hid, id_type=idtype, location='@sun', epochs=year).vectors(closest_apparition=(idtype == 'designation'))
    ax1.plot(v['x'], v['y'], label=label)
ax1.plot(0, 0, 'y*', ms=15); ax1.set_aspect('equal'); ax1.legend(); ax1.set_xlabel('x (au)'); ax1.set_ylabel('y (au)')
# Right: Apophis (99942) distance from Earth's centre around 13 Apr 2029, every 10 minutes
ap = Horizons(id='99942', id_type='smallbody', location='500@399',
              epochs={'start': '2029-04-12', 'stop': '2029-04-15', 'step': '10m'}).vectors()
hours = (ap['datetime_jd'] - ap['datetime_jd'][ap['range'].argmin()]) * 24
ax2.plot(hours, ap['range'] * 149597870.7, label='Apophis'); ax2.axhline(42164, ls='--', c='gray', label='geostationary satellites')
ax2.set_yscale('log'); ax2.set_xlabel('Hours from closest approach (2029 Apr 13)'); ax2.set_ylabel('Distance from Earth centre (km)'); ax2.legend()
plt.tight_layout(); plt.savefig('interstellar_apophis.png', dpi=150)
