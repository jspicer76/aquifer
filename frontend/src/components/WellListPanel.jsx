import { useWellsStore } from "../state/wells";

export default function WellListPanel({ selectedWellId, onSelect = () => {} }) {
  const wells = useWellsStore(state => state.wells);

  return (
    <section className="panel">
      <h3>Wells</h3>
      {Object.keys(wells).length === 0 && <p>No wells have been digitized yet.</p>}
      <ul>
        {Object.values(wells).map(well => (
          <li key={well.id}>
            <button
              className={well.id === selectedWellId ? "selected" : ""}
              onClick={() => onSelect(well.id)}
            >
              {well.type === "pumping" ? "Pumping" : "Observation"} @
              {well.lat.toFixed(4)}, {well.lng.toFixed(4)}
            </button>
          </li>
        ))}
      </ul>
    </section>
  );
}
