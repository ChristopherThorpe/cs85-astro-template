#!/bin/bash
# CS85 astronomy cloud environment: paste this into the environment's "Setup script" box.
# Runs once, then Claude caches the result, so later sessions start with everything installed.
pip install --break-system-packages -q \
  alerce astropy astroquery daschlab dkist drms gwpy lightkurve matplotlib numpy pandas \
  pyvo requests scikit-learn scipy skyfield sparclclient "sunpy[net]" plotly streamlit || true
