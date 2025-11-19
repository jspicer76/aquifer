import { create } from "zustand";

export const useUIStore = create(set => ({
  drawerOpen: false,
  drawerType: null,
  drawerWellId: null,
  drawerPayload: null,

  openDrawer: (type, payload = null) =>
    set({
      drawerOpen: true,
      drawerType: type,
      drawerWellId: payload?.wellId ?? null,
      drawerPayload: payload
    }),

  closeDrawer: () =>
    set({
      drawerOpen: false,
      drawerType: null,
      drawerWellId: null,
      drawerPayload: null
    })
}));
