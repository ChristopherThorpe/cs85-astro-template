#!/bin/bash
# CS85 astronomy cloud environment: paste this into the environment's "Setup script" box.
# Runs once, then Claude caches the result, so later sessions start with everything installed.
# --use-pep517 builds source-only packages (pims, fbpca, memoization) with a fresh setuptools;
# without it, the system's Debian setuptools fails with "AttributeError: install_layout".
pip install --break-system-packages -q --ignore-installed --use-pep517 pip setuptools wheel
pip install --break-system-packages -q --use-pep517 \
  alerce astropy astroquery daschlab dkist drms gwpy lightkurve matplotlib numpy pandas \
  pyvo requests scikit-learn scipy skyfield sparclclient "sunpy[net]" plotly streamlit \
  || echo "WARNING: CS85 setup pip install failed"
