import React, { useState, useEffect } from "react";

export default function BoundaryMetadataModal({
  open,
  mode,
  selected,
  onClose,
  onSubmit,
  onDelete,
  onEditGeometry
}) {
  const [head, setHead] = useState("");
  const [rate, setRate] = useState("");
  const [cond, setCond] = useState("");

  useEffect(() => {
    if (!open) {
      setHead("");
      setRate("");
      setCond("");
      return;
    }

    setHead(selected?.head ?? "");
    setRate(selected?.rate ?? "");
    setCond(selected?.cond ?? "");
  }, [open, selected]);

  if (!open || !mode) return null;

  const showHead = mode === "chb" || mode === "ghb";
  const showRate = mode === "recharge";
  const showCond = mode === "ghb";
  const isEditing = Boolean(selected);

  function save() {
    const meta = {};
    if (showHead) meta.head = head === "" ? null : parseFloat(head);
    if (showRate) meta.rate = rate === "" ? null : parseFloat(rate);
    if (showCond) meta.cond = cond === "" ? null : parseFloat(cond);

    if (onSubmit) {
      onSubmit(meta);
    }
  }

  return (
    <div style={backdrop}>
      <div style={modal}>
        <h3>{isEditing ? "Edit Boundary" : "Add Boundary"}</h3>

        {showHead && (
          <>
            <label>Boundary Head (ft)</label>
            <input value={head} onChange={e => setHead(e.target.value)} />
          </>
        )}

        {showRate && (
          <>
            <label>Recharge Rate (in/yr or gpd/ac)</label>
            <input value={rate} onChange={e => setRate(e.target.value)} />
          </>
        )}

        {showCond && (
          <>
            <label>Conductance (ft^2/day)</label>
            <input value={cond} onChange={e => setCond(e.target.value)} />
          </>
        )}

        <div style={{ marginTop: "20px" }}>
          <button onClick={save}>Save</button>
          {onEditGeometry && isEditing && (
            <button style={{ marginLeft: "10px" }} onClick={onEditGeometry}>
              Edit Geometry
            </button>
          )}
          {onDelete && isEditing && (
            <button
              style={{ marginLeft: "10px", background: "#c1121f", color: "white" }}
              onClick={onDelete}
            >
              Delete
            </button>
          )}
          <button style={{ marginLeft: "10px" }} onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

const backdrop = {
  position: "fixed",
  top: 0,
  left: 0,
  width: "100vw",
  height: "100vh",
  background: "rgba(0,0,0,0.4)",
  zIndex: 9999,
  display: "flex",
  justifyContent: "center",
  alignItems: "center"
};

const modal = {
  background: "white",
  padding: "20px",
  width: "340px",
  borderRadius: "6px",
  boxShadow: "0 3px 10px rgba(0,0,0,0.3)"
};
