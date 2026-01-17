import React from "react";

const Card = ({ id, name, good, bad, selected }) => {
  const handleDragStart = (e) => {
    if (selected) {
      e.preventDefault();
      return;
    }
    e.dataTransfer.setData(
      "application/json",
      JSON.stringify({ id, name, good, bad }),
    );
    e.dataTransfer.effectAllowed = "move";
  };

  return (
    <div
      draggable={!selected}
      onDragStart={handleDragStart}
      className={`
        w-36 aspect-[5/7] rounded-lg transition-all flex flex-col overflow-hidden shadow-lg
        ${
          selected
            ? "opacity-40 cursor-not-allowed ring-2 ring-amber-500"
            : "bg-neutral-800 hover:bg-neutral-700 hover:-translate-y-1 cursor-grab active:cursor-grabbing hover:shadow-xl"
        }
      `}
    >
      <div className="flex-1 bg-gradient-to-b from-neutral-700 to-neutral-800 flex items-center justify-center">
        <span className="text-5xl">🤖</span>
      </div>
      <div className="p-2 bg-neutral-900 space-y-1">
        <h3 className="text-white font-bold text-sm truncate">{name}</h3>
        <div className="flex flex-col gap-0.5 text-[10px]">
          <span className="text-green-400 truncate">+ {good}</span>
          <span className="text-red-400 truncate">− {bad}</span>
        </div>
      </div>
    </div>
  );
};

export default Card;
