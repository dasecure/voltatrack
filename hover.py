import streamlit as st
import pydeck as pdk

UK_ACCIDENTS_DATA = (
    "https://raw.githubusercontent.com/uber-common/"
    "deck.gl-data/master/examples/3d-heatmap/heatmap-data.csv"
)
layer = pdk.Layer(
    "HexagonLayer",
    UK_ACCIDENTS_DATA,
    get_position="[lng, lat]",
    auto_highlight=True,
    elevation_scale=50,
    pickable=True,
    elevation_range=[0, 3000],
    extruded=True,
    coverage=1,
)
# Set the viewport location
view_state = pdk.ViewState(
    longitude=-1.415, latitude=52.2323, zoom=6, min_zoom=5, max_zoom=15, pitch=40.5, bearing=-27.36
)
# Combined all of it and render a viewport
r = pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    layers=[layer],
    initial_view_state=view_state,
    tooltip={"html": "<b>Elevation Value:</b> {elevationValue}", "style": {"color": "white"}},
)
st.pydeck_chart(r)