import { create } from "zustand";

export const useResultsStore = create(set => ({
  results: null,
  setResults: results => set({ results }),
  clearResults: () => set({ results: null })
}));
