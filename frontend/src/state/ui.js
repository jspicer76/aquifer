import { create } from "zustand";

export const useUIStore = create(set => ({
  drawerOpen: false,
  drawerType: null,
  drawerWellId: null,


  openDrawer("results", { results })

  openDrawer: (type, wellId = null) =>
    set({
      drawerOpen: true,
      drawerType: type,
      drawerWellId: wellId
    }),

  closeDrawer: () =>
    set({
      drawerOpen: false,
      drawerType: null,
      drawerWellId: null
    })
}));
