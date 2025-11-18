import React from "react";
import L from "leaflet";
import { Marker, Popup } from "react-leaflet";

const pumpIcon = new L.Icon({
    iconUrl: "/pump.png",
    iconSize: [32, 32],
});

const obsIcon = new L.Icon({
    iconUrl: "/obs.png",
    iconSize: [28, 28],
});

export default function WellMarker({ well }) {
    return (
        <Marker
            position={[well.lat, well.lng]}
            icon={well.type === "pumping" ? pumpIcon : obsIcon}
        >
            <Popup>
                <b>{well.type.toUpperCase()} WELL</b><br />
                Lat: {well.lat}<br />
                Lng: {well.lng}
            </Popup>
        </Marker>
    );
}
