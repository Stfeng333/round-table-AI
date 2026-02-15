import React, { useState } from "react";

const MODEL_LOGOS = {
  Gemini: "/logos/gemini.png",
  Llama: "/logos/llama.png",
  Qwen: "/logos/qwen.png",
  ChatGPT: "/logos/chatgpt.png",
  Kimi: "/logos/kimi.png",
};

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
        className={`flex gap-3 p-2 rounded-lg transition-colors ${isDragOver ? "bg-amber-500/10" : ""}`}
      >
        {slots.map((_, i) => (
          <div
            key={i}
            onClick={() => selected[i] && onRemove?.(selected[i])}
            className={`
              w-28 aspect-[5/7] rounded-lg overflow-hidden transition-all relative
              ${
                selected[i]
                  ? "cursor-pointer hover:ring-2 hover:ring-red-500"
                  : "bg-neutral-800 border border-dashed border-neutral-600"
              }
              ${isDragOver && !selected[i] ? "border-amber-500 bg-amber-500/10" : ""}
            `}
          >
            {selected[i] ? (
              <>
                <div className="absolute inset-0 bg-neutral-200 flex items-center justify-center pb-12">
                  <img
                    src={MODEL_LOGOS[selected[i].model]}
                    alt={selected[i].model}
                    className="w-16 h-16 object-contain"
                  />
                </div>
                <div className="absolute bottom-0 left-0 right-0 p-1.5 bg-neutral-900 space-y-0.5">
                  <h3 className="text-white font-bold text-[10px] truncate">
                    {selected[i].model}
                  </h3>
                  <div className="flex flex-col text-[8px]">
                    <span className="text-blue-400 truncate">
                      🎯 {selected[i].expertise}
                    </span>
                    <span className="text-purple-400 truncate">
                      💭 {selected[i].personality}
                    </span>
                  </div>
                </div>
              </>
            ) : (
              <div className="w-full h-full flex items-center justify-center">
                <span className="text-neutral-600 text-lg">+</span>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default RoleSlot;
