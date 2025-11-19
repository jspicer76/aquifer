import { create } from "zustand";

const DEFAULT_AQUIFER = {
  b: 65,
  annual_precip_in: 47,
  infiltration_fraction: 0.2
};

export const useAquiferStore = create(set => ({
  aquifer: DEFAULT_AQUIFER,
  updateAquifer: updates =>
    set(state => ({
      aquifer: { ...state.aquifer, ...updates }
    })),
  resetAquifer: () => set({ aquifer: DEFAULT_AQUIFER })
}));
