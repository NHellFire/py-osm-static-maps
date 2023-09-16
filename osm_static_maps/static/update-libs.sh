#!/bin/sh
LEAFLET_VERSION=1.9.4
LEAFLET_FILES="leaflet.min.css leaflet.min.js images/layers.png images/layers-2x.png images/marker-icon.png images/marker-icon-2x.png images/marker-shadow.png"

MAPBOX_GL_VERSION=2.15.0
MAPBOX_GL_FILES="mapbox-gl.js mapbox-gl.css"

MAPBOX_GL_LEAFLET_VERSION=0.0.16
MAPBOX_GL_LEAFLET_FILES="leaflet-mapbox-gl.min.js"

LEAFLET_POLYLINE_VERSION=1.6.0
LEAFLET_POLYLINE_FILES="leaflet.polylineDecorator.js"

for file in ${LEAFLET_FILES}; do
	curl -f -L --etag-save "${file}.etag" --etag-compare "${file}.etag" -o "${file}" "https://cdnjs.cloudflare.com/ajax/libs/leaflet/${LEAFLET_VERSION}/${file}"
done

for file in ${MAPBOX_GL_FILES}; do
	curl -f -L --etag-save "${file}.etag" --etag-compare "${file}.etag" -o "${file}" "https://api.mapbox.com/mapbox-gl-js/v${MAPBOX_GL_VERSION}/${file}"
done

for file in ${MAPBOX_GL_LEAFLET_FILES}; do
	curl -f -L --etag-save "${file}.etag" --etag-compare "${file}.etag" -o "${file}" "https://cdnjs.cloudflare.com/ajax/libs/mapbox-gl-leaflet/${MAPBOX_GL_LEAFLET_VERSION}/${file}"
done

for file in ${LEAFLET_POLYLINE_FILES}; do
	curl -f -L --etag-save "${file}.etag" --etag-compare "${file}.etag" -o "${file}" "https://github.com/bbecquet/Leaflet.PolylineDecorator/raw/v${LEAFLET_POLYLINE_VERSION}/dist/${file}"
done

