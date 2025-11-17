import { create } from "zustand";
import { v4 as uuid } from "uuid";

export const useWellsStore = create(set => ({
    wells: {},

    addWell: (type, lat, lng) =>
        set(state => {
            const id = uuid();
            return {
                wells: {
                    ...state.wells,
                    [id]: {
                        id,
                        type,
                        lat,
                        lng,
                        data: {}  // properties added later
                    }
                }
            };
        }),

    updateWellData: (id, newData) =>
        set(state => ({
            wells: {
                ...state.wells,
                [id]: {
                    ...state.wells[id],
                    data: { ...state.wells[id].data, ...newData }
                }
            }
        })),

    removeWell: id =>
        set(state => {
            const updated = { ...state.wells };
            delete updated[id];
            return { wells: updated };
        })
}));
