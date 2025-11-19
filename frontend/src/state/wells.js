import { create } from "zustand";
import { v4 as uuid } from "uuid";

export const useWellsStore = create((set, get) => ({
  wells: [],
  mode: null,
  isRunning: false,
  lastRunSummary: null,
  error: null,

  addPumpingWell: () => set({ mode: "pumping" }),
  addObservationWell: () => set({ mode: "observation" }),
  clearMode: () => set({ mode: null }),

  addWell: (type, lat, lng) =>
    set((state) => ({
      wells: [
        ...state.wells,
        {
          id: uuid(),
          type, // "pumping" or "observation"
          lat,
          lng,
          data: {}
        }
      ],
      mode: null
    })),

  updateWellData: (id, newData) =>
    set((state) => ({
      wells: state.wells.map((w) =>
        w.id === id
          ? {
              ...w,
              data: { ...w.data, ...newData }
            }
          : w
      )
    })),

  removeWell: (id) =>
    set((state) => ({
      wells: state.wells.filter((w) => w.id !== id)
    })),

  clearWells: () =>
    set({
      wells: [],
      mode: null
    }),

  runModel: async () => {
    const wells = get().wells;
    if (!wells.length) {
      set({ error: "Add at least one well before running the aquifer model." });
      return;
    }

    set({ isRunning: true, error: null });

    try {
      const response = await fetch("/api/model/run", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ wells })
      });

      if (!response.ok) {
        const message = await response.text();
        throw new Error(message || `Model request failed (${response.status}).`);
      }

      const payload = await response.json();
      set({
        isRunning: false,
        lastRunSummary: payload.summary ?? null,
        error: null
      });
    } catch (err) {
      set({
        isRunning: false,
        error: err.message || "Unable to run aquifer model."
      });
    }
  }
}));
