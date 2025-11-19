import { create } from "zustand";

const DEFAULT_DEMAND = {
  population: 2500,
  gpcd: 100,
  curve: [1.2, 1.1, 1.05, 1.0, 0.9, 0.85, 0.9, 1.05, 1.2, 1.35, 1.3, 1.15, 1.0]
};

export const useDemandStore = create(set => ({
  demand: DEFAULT_DEMAND,
  updateDemand: updates =>
    set(state => ({
      demand: { ...state.demand, ...updates }
    })),
  resetDemand: () => set({ demand: DEFAULT_DEMAND })
}));
