import React, { useState } from "react";

const RoleSlot = ({ role, selected, required, onDrop, onRemove }) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const filled = selected.length;
  const slots = Array(required).fill(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    if (filled < required) {
      e.dataTransfer.dropEffect = "move";
      setIsDragOver(true);
    }
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    if (filled >= required) return;

    try {
      const cardData = JSON.parse(e.dataTransfer.getData("application/json"));
      onDrop?.(cardData);
    } catch (err) {
      console.error("Drop error:", err);
    }
  };

  return (
    <div
      className="flex flex-col"
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      <div className="flex items-center gap-2 mb-2">
        <span className="text-white text-sm font-bold uppercase tracking-wide">
          {role}
        </span>
        <span
          className={`text-xs font-medium ${filled === required ? "text-amber-400" : "text-neutral-600"}`}
        >
          {filled}/{required}
        </span>
      </div>
      <div
        className={`flex gap-2 p-2 rounded-lg transition-colors ${isDragOver ? "bg-amber-500/10" : ""}`}
      >
        {slots.map((_, i) => (
          <div
            key={i}
            onClick={() => selected[i] && onRemove?.(selected[i])}
            className={`
              w-14 aspect-[5/7] rounded flex items-center justify-center transition-all
              ${
                selected[i]
                  ? "bg-neutral-700 cursor-pointer hover:bg-red-900/50"
                  : "bg-neutral-800 border border-dashed border-neutral-600"
              }
              ${isDragOver && !selected[i] ? "border-amber-500 bg-amber-500/10" : ""}
            `}
          >
            {selected[i] ? (
              <span className="text-lg">🤖</span>
            ) : (
              <span className="text-neutral-600 text-lg">+</span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default RoleSlot;
