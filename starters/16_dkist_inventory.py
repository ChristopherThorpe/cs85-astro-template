# pip install dkist pandas matplotlib
# --- Setup: make sure the packages this script needs are installed. ----------------------
# Cloud sessions install them in the background when they start. This waits for that to
# finish, then installs anything still missing. (On your own computer it just installs them.)
import importlib, importlib.util, os, subprocess, sys, tempfile
NEEDED = {"sunpy": "sunpy[net]", "drms": "sunpy[net]", "zeep": "sunpy[net]", "dkist": "dkist"}   # module name: pip package name
                                     # (sunpy's search tools also need drms and zeep)
try:
    import fcntl   # file locks, to wait for the background install (not available on Windows)
    lock = open(os.path.join(tempfile.gettempdir(), "cs85-extras.lock"), "a")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print("Waiting for the background install of the solar and DASCH packages...", flush=True)
        fcntl.flock(lock, fcntl.LOCK_EX)
except ImportError:
    lock = None
importlib.invalidate_caches()
missing = sorted({pkg for mod, pkg in NEEDED.items() if importlib.util.find_spec(mod) is None})
if missing:
    print("Installing", ", ".join(missing), "(about a minute)...", flush=True)
    subprocess.run([sys.executable, "-m", "pip", "install", *missing], check=True)
if lock:
    lock.close()   # done: let other scripts (or the background install) go ahead
# ------------------------------------------------------------------------------------------
import dkist.net                     # registers the DKIST Data Center search with sunpy's Fido (no login needed)
import pandas as pd, matplotlib.pyplot as plt
from sunpy.net import Fido, attrs as a
rows = []
for page in range(1, 100):           # the archive returns datasets 300 per page
    t = Fido.search(a.Time('2022-01-01', '2026-12-31'), a.dkist.Page(page), a.dkist.PageSize(300))[0]
    if len(t) == 0: break
    rows += [dict(inst=r['Instrument'], start=str(r['Start Time']), nm=r['Wavelength'][0].to_value('nm'),
                  embargoed=r['Embargoed']) for r in t]
    if len(rows) >= t.total_available_results: break
df = pd.DataFrame(rows); df['start'] = pd.to_datetime(df['start'])
print(len(df), 'datasets'); print(df.groupby(['inst', 'embargoed']).size())   # public vs. embargoed per instrument
fig, ax = plt.subplots(figsize=(10, 5))
for inst, g in df.groupby('inst'): ax.scatter(g['start'], g['nm'], s=12, alpha=0.6, label=inst)
ax.set(yscale='log', xlabel='Observation start (UT)', ylabel='Wavelength (nm)', title='Every DKIST Level-1 dataset in the archive')
ax.legend(); plt.savefig('dkist_inventory.png', dpi=150)
