import React, { useRef } from "react";

const MODEL_LOGOS = {
  Gemini: "/logos/gemini.png",
  Llama: "/logos/llama.png",
  Qwen: "/logos/qwen.png",
  ChatGPT: "/logos/chatgpt.png",
  Kimi: "/logos/kimi.png",
};

const Card = ({ id, model, expertise, personality, selected }) => {
  const cardRef = useRef(null);

  const handleDragStart = (e) => {
    if (selected) {
      e.preventDefault();
      return;
    }
    e.dataTransfer.setData(
      "application/json",
      JSON.stringify({ id, model, expertise, personality }),
    );
    e.dataTransfer.effectAllowed = "move";

    // Create a custom drag image that's not transparent
    if (cardRef.current) {
      const rect = cardRef.current.getBoundingClientRect();
      e.dataTransfer.setDragImage(
        cardRef.current,
        rect.width / 2,
        rect.height / 2,
      );
    }
  };

  return (
    <div
      ref={cardRef}
      draggable={!selected}
      onDragStart={handleDragStart}
      className={`
        w-36 aspect-[5/7] rounded-lg transition-all flex flex-col overflow-hidden shadow-lg relative
        ${
          selected
            ? "opacity-40 cursor-not-allowed ring-2 ring-amber-500"
            : "bg-neutral-800 hover:bg-neutral-700 hover:-translate-y-1 cursor-grab active:cursor-grabbing hover:shadow-xl"
        }
      `}
      style={{ WebkitUserDrag: "element" }}
    >
      <div className="absolute inset-0 bg-gradient-to-b from-neutral-300 to-neutral-400 flex items-center justify-center pb-16">
        <img
          src={MODEL_LOGOS[model]}
          alt={model}
          className="w-24 h-24 object-contain drop-shadow-md"
          draggable={false}
        />
      </div>
      <div className="absolute bottom-0 left-0 right-0 p-2 bg-neutral-900 space-y-1">
        <h3 className="text-white font-bold text-sm truncate">{model}</h3>
        <div className="flex flex-col gap-0.5 text-xs">
          <span className="text-blue-400 truncate">🎯 {expertise}</span>
          <span className="text-purple-400 truncate">💭 {personality}</span>
        </div>
      </div>
    </div>
  );
};

export default Card;
