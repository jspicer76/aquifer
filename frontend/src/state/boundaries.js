import { create } from "zustand";

export const useBoundaryStore = create((set, get) => ({
  // ---------------------------------------------------
  // DRAW & EDIT MODES
  // ---------------------------------------------------
  drawMode: null,           // "chb" | "noflow" | "recharge" | "ghb"
  editMode: false,
  drawingEnabled: false,

  // ---------------------------------------------------
  // BOUNDARY STORAGE
  // ---------------------------------------------------
  constantHead: [],     // { id, points[], head }
  noFlow: [],           // { id, points[] }
  rechargeZones: [],    // { id, polygon[], rate }
  generalHead: [],      // { id, points[], head, cond }

  // ---------------------------------------------------
  // START DRAWING
  // ---------------------------------------------------
  startDraw: (mode) =>
    set(() => ({
      drawMode: mode,
      drawingEnabled: true,
      editMode: false
    })),

  // ---------------------------------------------------
  // ENABLE EDITING (Leaflet.Draw edit mode)
  // ---------------------------------------------------
  startEdit: () =>
    set(() => ({
      editMode: true,
      drawingEnabled: false,
      drawMode: null
    })),

  stopDraw: () =>
    set(() => ({
      drawMode: null,
      drawingEnabled: false
    })),

  stopEdit: () =>
    set(() => ({
      editMode: false
    })),

  // ---------------------------------------------------
  // ADD NEW BOUNDARY AFTER DRAWING
  // ---------------------------------------------------
  addBoundary: (mode, geometry, metadata = {}) =>
    set((state) => {
      const id = crypto.randomUUID();

      switch (mode) {
        case "chb":
          return {
            constantHead: [
              ...state.constantHead,
              { id, points: geometry, head: metadata.head ?? null }
            ],
            drawMode: null,
            drawingEnabled: false
          };
        case "noflow":
          return {
            noFlow: [...state.noFlow, { id, points: geometry }],
            drawMode: null,
            drawingEnabled: false
          };
        case "recharge":
          return {
            rechargeZones: [
              ...state.rechargeZones,
              { id, polygon: geometry, rate: metadata.rate ?? 0 }
            ],
            drawMode: null,
            drawingEnabled: false
          };
        case "ghb":
          return {
            generalHead: [
              ...state.generalHead,
              {
                id,
                points: geometry,
                head: metadata.head ?? null,
                cond: metadata.cond ?? null
              }
            ],
            drawMode: null,
            drawingEnabled: false
          };
        default:
          console.warn("Unknown boundary mode:", mode);
          return {};
      }
    }),

  // ---------------------------------------------------
  // UPDATE BOUNDARY METADATA (head, cond, rate)
  // ---------------------------------------------------
  updateMetadata: (type, id, newData) =>
    set((state) => ({
      [type]: state[type].map((b) =>
        b.id === id ? { ...b, ...newData } : b
      )
    })),

  // ---------------------------------------------------
  // REPLACE GEOMETRY (after editing)
  // ---------------------------------------------------
  updateGeometry: (type, id, newGeometry) =>
    set((state) => ({
      [type]: state[type].map((b) =>
        b.id === id
          ? {
              ...b,
              points: newGeometry,
              polygon: newGeometry // for recharge
            }
          : b
      )
    })),

  // ---------------------------------------------------
  // REMOVE BOUNDARY
  // ---------------------------------------------------
  removeBoundary: (type, id) =>
    set((state) => ({
      [type]: state[type].filter((b) => b.id !== id)
    })),

  // ---------------------------------------------------
  // CLEAR TYPE
  // ---------------------------------------------------
  clearType: (type) =>
    set(() => ({
      [type]: []
    })),

  // ---------------------------------------------------
  // EXPORT BOUNDARIES TO BACKEND FORMAT
  // ---------------------------------------------------
  exportForBackend: () => {
    const state = get();

    return {
      constant_head: state.constantHead.map((b) => ({
        points: b.points,
        head: b.head
      })),

      no_flow: state.noFlow.map((b) => ({
        points: b.points
      })),

      recharge_zones: state.rechargeZones.map((b) => ({
        polygon: b.polygon,
        rate: b.rate
      })),

      general_head: state.generalHead.map((b) => ({
        points: b.points,
        head: b.head,
        cond: b.cond
      }))
    };
  },

  // ---------------------------------------------------
  // CLEAR ALL
  // ---------------------------------------------------
  clearAll: () =>
    set(() => ({
      constantHead: [],
      noFlow: [],
      rechargeZones: [],
      generalHead: [],
      drawMode: null,
      drawingEnabled: false,
      editMode: false
    }))
}));
