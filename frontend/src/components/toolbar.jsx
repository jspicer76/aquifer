import React from "react";
import { useWellsStore } from "../state/wells";

export default function Toolbar() {
    const addPumpingWell = useWellsStore(s => s.addPumpingWell);
    const addObservationWell = useWellsStore(s => s.addObservationWell);
    const runModel = useWellsStore(s => s.runModel);

    return (
        <div className="toolbar">
            <button onClick={addPumpingWell}>Add Pumping Well</button>
            <button onClick={addObservationWell}>Add Observation Well</button>
            <button onClick={runModel}>Run Aquifer Model</button>
        </div>
    );
}
