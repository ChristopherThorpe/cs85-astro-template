# pip install drms pandas matplotlib
# --- Setup: make sure the packages this script needs are installed. ----------------------
# Cloud sessions install them in the background when they start. This waits for that to
# finish, then installs anything still missing. (On your own computer it just installs them.)
import importlib, importlib.util, os, subprocess, sys, tempfile
NEEDED = {"drms": "drms"}   # module name: pip package name
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
import drms, pandas as pd, matplotlib.pyplot as plt
c = drms.Client()   # keyword queries are anonymous; only image/FITS exports need a JSOC-registered email
# HARP 7115 = NOAA AR 12673 (X9.3 flare 2017-09-06). One record per hour for 15 days, good-quality records only
k = c.query('hmi.sharp_720s[7115][2017.08.28_TAI/15d@1h][? (QUALITY<65536) ?]',
            key='T_REC,USFLUX,TOTUSJH,LON_FWT,NOAA_AR')
k['time'] = drms.to_datetime(k['T_REC'])
k = k[k['LON_FWT'].abs() < 70]                       # drop records too close to the limb (projection effects)
fig, ax1 = plt.subplots(figsize=(10, 5))
ax1.plot(k['time'], k['USFLUX'], 'b'); ax1.set_ylabel('Total unsigned flux USFLUX (Mx)', color='b')
ax2 = ax1.twinx(); ax2.plot(k['time'], k['TOTUSJH'], 'r'); ax2.set_ylabel('Total unsigned current helicity TOTUSJH (G²/m)', color='r')
ax1.axvline(pd.Timestamp('2017-09-06 12:02'), color='k', ls='--', label='X9.3 flare peak'); ax1.legend(loc='upper left')
ax1.set_title(f"SDO/HMI SHARP 7115 (NOAA {k['NOAA_AR'].iloc[0]}) across the disk")
fig.autofmt_xdate(); plt.tight_layout(); plt.savefig('sharp_keywords.png', dpi=150)
