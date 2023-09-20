#!/bin/sh
LEAFLET_VERSION=1.9.4
LEAFLET_FILES="leaflet.min.css leaflet.min.js images/layers.png images/layers-2x.png images/marker-icon.png images/marker-icon-2x.png images/marker-shadow.png"

MAPLIBRE_GL_VERSION=3.3.1
MAPLIBRE_GL_FILES="maplibre-gl.js maplibre-gl.css"

MAPLIBRE_GL_LEAFLET_VERSION=0.0.20
MAPLIBRE_GL_LEAFLET_FILES="leaflet-maplibre-gl.js"

LEAFLET_POLYLINE_VERSION=1.6.0
LEAFLET_POLYLINE_FILES="leaflet.polylineDecorator.js"

for file in ${LEAFLET_FILES}; do
	curl -f -L --etag-save "${file}.etag" --etag-compare "${file}.etag" -o "${file}" "https://cdnjs.cloudflare.com/ajax/libs/leaflet/${LEAFLET_VERSION}/${file}"
done

for file in ${MAPLIBRE_GL_FILES}; do
	curl -f -L --etag-save "${file}.etag" --etag-compare "${file}.etag" -o "${file}" "https://unpkg.com/maplibre-gl@${MAPLIBRE_GL_VERSION}/dist/${file}"
done

for file in ${MAPLIBRE_GL_LEAFLET_FILES}; do
	curl -f -L --etag-save "${file}.etag" --etag-compare "${file}.etag" -o "${file}" "https://unpkg.com/@maplibre/maplibre-gl-leaflet@${MAPLIBRE_GL_LEAFLET_VERSION}/${file}"
done

for file in ${LEAFLET_POLYLINE_FILES}; do
	curl -f -L --etag-save "${file}.etag" --etag-compare "${file}.etag" -o "${file}" "https://github.com/bbecquet/Leaflet.PolylineDecorator/raw/v${LEAFLET_POLYLINE_VERSION}/dist/${file}"
done

