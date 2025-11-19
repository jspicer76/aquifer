import { motion, AnimatePresence } from "framer-motion";
import { useUIStore } from "../state/ui";
import PumpingWellEditor from "./drawer/PumpingWellEditor";
import ObservationWellEditor from "./drawer/ObservationWellEditor";
import AquiferSettings from "./drawer/AquiferSettings";
import DemandSettings from "./drawer/DemandSettings";
import ResultsDrawer from "./drawer/ResultsDrawer";

export default function RightDrawer() {
    const drawerOpen = useUIStore(s => s.drawerOpen);
    const drawerType = useUIStore(s => s.drawerType);
    const closeDrawer = useUIStore(s => s.closeDrawer);

    return (
        <AnimatePresence>
            {drawerOpen && (
                <>
                    {/* Dim background */}
                    <motion.div
                        className="drawer-backdrop"
                        style={{
                            position: "fixed",
                            inset: 0,
                            background: "rgba(0,0,0,0.3)",
                            zIndex: 9998
                        }}
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={closeDrawer}
                    />

                    {/* Drawer panel */}
                    <motion.div
                        className="drawer-panel"
                        style={{
                            position: "fixed",
                            top: 0,
                            right: 0,
                            width: "420px",
                            height: "100vh",
                            background: "white",
                            boxShadow: "-4px 0 12px rgba(0,0,0,0.15)",
                            padding: "20px",
                            zIndex: 9999,
                            overflowY: "auto"
                        }}
                        initial={{ x: 500 }}
                        animate={{ x: 0 }}
                        exit={{ x: 500 }}
                        transition={{ type: "spring", stiffness: 120 }}
                    >
                        {drawerType === "pumping" && <PumpingWellEditor />}
                        {drawerType === "observation" && <ObservationWellEditor />}
                        {drawerType === "aquifer" && <AquiferSettings />}
                        {drawerType === "demand" && <DemandSettings />}
                        {drawerType === "results" && <ResultsDrawer />}
                    </motion.div>
                </>
            )}
        </AnimatePresence>
    );
}
