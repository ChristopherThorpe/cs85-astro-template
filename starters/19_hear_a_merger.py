# pip install gwpy matplotlib requests
import os, requests
from gwpy.timeseries import TimeSeries

gps = 1126259462.4   # GW150914 merger time (GPS seconds)
# 32 s of LIGO-Livingston strain: GWOSC's 32-s event file (~1 MB download).
# We download it with requests (not TimeSeries.fetch_open_data) because requests uses the
# certificate list the class cloud environment sets up; gwpy's downloader ignores it.
url = ('https://gwosc.org/eventapi/json/GWTC-1-confident/GW150914/v3/'
       'L-L1_GWOSC_4KHZ_R1-1126259447-32.hdf5')
path = os.path.join('data', os.path.basename(url))
if not os.path.exists(path):                       # only download once
    os.makedirs('data', exist_ok=True)
    r = requests.get(url, timeout=120)
    r.raise_for_status()                           # stop with a clear error if the download failed
    open(path, 'wb').write(r.content)
data = TimeSeries.read(path, format='hdf5.gwosc')  # LIGO-Livingston strain, 4096 samples/s

q = data.q_transform(outseg=(gps - 0.5, gps + 0.2), frange=(20, 500))   # whitened time-frequency map
plot = q.plot(figsize=(8, 4))
ax = plot.gca()
ax.set_xscale('seconds'); ax.set_epoch(gps)          # time axis = seconds relative to the merger
ax.set_yscale('log'); ax.set_ylim(20, 500); ax.set_ylabel('Frequency [Hz]')
ax.set_title('GW150914 at LIGO Livingston: two black holes merging')
ax.colorbar(cmap='viridis', label='Normalized energy')
plot.savefig('hear_a_merger.png', dpi=150, bbox_inches='tight')

# Bonus: make it audible -> whiten, keep 30-400 Hz, 3 s around the merger, save as WAV
data.whiten(4, 2).bandpass(30, 400).crop(gps - 2, gps + 1).write('GW150914.wav')
