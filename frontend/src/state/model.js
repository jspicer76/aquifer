import { create } from "zustand";
import { useWellsStore } from "./wells";
import { useAquiferStore } from "./aquifer";
import { useDemandStore } from "./demand";
import { useResultsStore } from "./results";
import { useUIStore } from "./ui";

export const useModelRunner = create(set => ({
  loading: false,
  error: null,

    runModel: async () => {
      const wells = useWellsStore.getState().wells;
      const aquifer = useAquiferStore.getState().aquifer;
      const demand = useDemandStore.getState().demand;

      const setResults = useResultsStore.getState().setResults;
      const openDrawer = useUIStore.getState().openDrawer;

      const payload = {
        wells: Object.values(wells),
        aquifer,
        demand
      };

      set({ loading: true, error: null });

      try {
        // -------------------------------
        // MAIN MODEL RUN
        // -------------------------------
        const response = await fetch("http://127.0.0.1:8000/run_model", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });

        if (!response.ok) throw new Error("Model failed");
        const data = await response.json();

        // -------------------------------
        // FETCH WHP CAPTURE ZONES (GEOJSON)
        // -------------------------------
        const whpRes = await fetch("http://127.0.0.1:8000/whp_geojson", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });

        const whpGeo = await whpRes.json();
        data.whp_geojson = whpGeo; // attach WHP polygons to main result

        // -------------------------------
        // SAVE & SHOW IN RESULTS DRAWER
        // -------------------------------
        setResults(data);
        openDrawer("results");

        set({ loading: false });

      } catch (err) {
        console.error(err);
        set({ loading: false, error: "Failed to run model" });
      }
  }

}));
