import { MapContainer, TileLayer, Marker, useMapEvents } from "react-leaflet";
import L from "leaflet";
import { useWellsStore } from "../state/wells";
import pumpIcon from "../assets/pump_icon.png";
import obsIcon from "../assets/obs_icon.png";

const PumpIcon = L.icon({ iconUrl: pumpIcon, iconSize: [32, 32] });
const ObsIcon = L.icon({ iconUrl: obsIcon, iconSize: [28, 28] });

export default function MapView() {
    const addWell = useWellsStore(state => state.addWell);
    const wells = useWellsStore(state => state.wells);

    function MapClickHandler() {
        useMapEvents({
            click(e) {
                const { lat, lng } = e.latlng;
                const type = window.prompt("Enter well type (pumping/observation)");
                if (type === "pumping" || type === "observation") {
                    addWell(type, lat, lng);
                }
            }
        });
        return null;
    }

    return (
        <MapContainer center={[38.2, -85.9]} zoom={12} style={{ height: "100vh" }}>
            <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />

            <MapClickHandler />

            {Object.values(wells).map(well => (
                <Marker
                    key={well.id}
                    position={[well.lat, well.lng]}
                    icon={well.type === "pumping" ? PumpIcon : ObsIcon}
                />
            ))}
        </MapContainer>
    );
}
