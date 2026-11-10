# pip install daschlab matplotlib
# --- Setup: make sure the packages this script needs are installed. ----------------------
# Cloud sessions install them in the background when they start. This waits for that to
# finish, then installs anything still missing. (On your own computer it just installs them.)
import importlib, importlib.util, os, subprocess, sys, tempfile
NEEDED = {"daschlab": "daschlab"}   # module name: pip package name
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
import matplotlib.pyplot as plt
from daschlab import open_session

sess = open_session(source="T CrB")  # makes a folder daschlab_t_crb/ that caches all downloads
sess.select_target(name="T CrB").select_refcat("apass")
lc = sess.lightcurve(0)  # 0 = catalog star closest to the target
lc.apply_standard_rejections()  # flag known-bad plate measurements
det, lim = lc.drop.rejected(verbose=False).split_by.detected()

plt.figure(figsize=(10, 4))
plt.scatter(lim["time"].jyear, lim["limiting_mag_local"], marker="v", s=6, c="lightgray", label="not seen (fainter than)")
plt.scatter(det["time"].jyear, det["magcal_magdep"], s=4, c="k", label="measured")
plt.gca().invert_yaxis()
plt.xlabel("Year"); plt.ylabel("Calibrated magnitude (blue plates)")
plt.title("T Coronae Borealis on Harvard glass plates (DASCH DR7)"); plt.legend()
plt.savefig("dasch_century.png", dpi=150)
