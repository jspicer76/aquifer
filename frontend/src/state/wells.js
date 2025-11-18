import { create } from "zustand";
import { v4 as uuid } from "uuid";

export const useWellsStore = create((set) => ({
  wells: [],   // MUST BE AN ARRAY

  addWell: (type, lat, lng) =>
    set((state) => {
      const id = uuid();
      return {
        wells: [
          ...state.wells,
          {
            id,
            type,          // "pumping" or "observation"
            lat,
            lng,
            data: {}       // additional well properties go here
          }
        ]
      };
    }),

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

  clearWells: () => set({ wells: [] })
}));
