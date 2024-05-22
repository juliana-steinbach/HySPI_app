import streamlit as st
import geemap.foliumap as geemap
import ee
import os
os.environ['EARTHENGINE_TOKEN'] = '1//03jrOgJyJRsYeCgYIARAAGAMSNwF-L9IrZcFiXw-FJxUYZSjN97jpdy5sBaN0LQUcm6fw7VZhcf0pjkxduhE1ZSW5LD4s320owzw'

st.set_page_config(layout="wide")

# Customize the sidebar
markdown = """
Web App URL: <https://geemap.streamlit.app>
"""

# Customize page title
st.title("Earth Engine Web App")

st.markdown(
    """
    This multipage app template demonstrates various interactive web apps created using [streamlit](https://streamlit.io) and [geemap](https://geemap.org). It is an open-source project and you are very welcome to contribute to the [GitHub repository](https://github.com/giswqs/geemap-apps).
    """
)

st.header("Instructions")

markdown = """
1. For the [GitHub repository](https://github.com/giswqs/geemap-apps) or [use it as a template](https://github.com/new?template_name=geemap-apps&template_owner=giswqs) for your own project.
2. Customize the sidebar by changing the sidebar text and logo in each Python files.
3. Find your favorite emoji from https://emojipedia.org.
4. Add a new app to the `pages/` directory with an emoji in the file name, e.g., `1_🚀_Chart.py`.
"""

st.markdown(markdown)

m = geemap.Map(location=[46.903354, 2.088334], zoom_start=6)
m.add_basemap("OpenTopoMap")
m.to_streamlit(height=500)

