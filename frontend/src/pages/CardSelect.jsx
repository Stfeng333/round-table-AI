import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import Card from "../components/CardSelect/Card";
import RoleSlot from "../components/CardSelect/RoleSlot";
import Button from "../components/common/Button";

const MODELS = ["Gemini", "Llama", "Qwen", "ChatGPT", "Kimi"];

const EXPERTISE = [
  "Pattern Recognition",
  "Risk Assessment",
  "Creative Thinking",
  "Decision Making",
  "Long-Term Vision",
  "Detail Focus",
];

const PERSONALITIES = [
  "Dominant",
  "Leader",
  "Thoughtful",
  "Analytical",
  "Creative",
  "Aggressive",
  "Cautious",
  "Patient",
  "Decisive",
  "Flexible",
  "Detail-Oriented",
];

// Seeded random for consistent attributes per card
const seededRandom = (seed) => {
  const x = Math.sin(seed) * 10000;
  return x - Math.floor(x);
};

const getRandomAttributes = (cardId) => {
  const seed = parseInt(cardId) * 137;
  const modelIndex = Math.floor(seededRandom(seed) * MODELS.length);
  const expertiseIndex = Math.floor(seededRandom(seed + 1) * EXPERTISE.length);
  const personalityIndex = Math.floor(
    seededRandom(seed + 2) * PERSONALITIES.length,
  );

  return {
    model: MODELS[modelIndex],
    expertise: EXPERTISE[expertiseIndex],
    personality: PERSONALITIES[personalityIndex],
  };
};

// Generate cards with random attributes
const ALL_CARDS = [
  { id: "1", ...getRandomAttributes("1") },
  { id: "2", ...getRandomAttributes("2") },
  { id: "3", ...getRandomAttributes("3") },
  { id: "4", ...getRandomAttributes("4") },
  { id: "5", ...getRandomAttributes("5") },
  { id: "6", ...getRandomAttributes("6") },
  { id: "7", ...getRandomAttributes("7") },
  { id: "8", ...getRandomAttributes("8") },
  { id: "9", ...getRandomAttributes("9") },
  { id: "10", ...getRandomAttributes("10") },
  { id: "11", ...getRandomAttributes("11") },
  { id: "12", ...getRandomAttributes("12") },
  { id: "13", ...getRandomAttributes("13") },
  { id: "14", ...getRandomAttributes("14") },
  { id: "15", ...getRandomAttributes("15") },
  { id: "16", ...getRandomAttributes("16") },
  { id: "17", ...getRandomAttributes("17") },
  { id: "18", ...getRandomAttributes("18") },
  { id: "19", ...getRandomAttributes("19") },
  { id: "20", ...getRandomAttributes("20") },
  { id: "21", ...getRandomAttributes("21") },
  { id: "22", ...getRandomAttributes("22") },
  { id: "23", ...getRandomAttributes("23") },
  { id: "24", ...getRandomAttributes("24") },
];

const ROLE_REQUIREMENTS = {
  facilitator: 1,
  critic: 1,
  stateTracker: 2,
  reasoner: 2,
};

const CardSelect = () => {
  const navigate = useNavigate();
  const [selectedCards, setSelectedCards] = useState({
    facilitator: [],
    critic: [],
    stateTracker: [],
    reasoner: [],
  });
  const [isCollapsed, setIsCollapsed] = useState(false);

  const handleDrop = (roleKey, card) => {
    const current = selectedCards[roleKey];
    const max = ROLE_REQUIREMENTS[roleKey];

    // Check if card is already in any slot
    const isAlreadySelected = Object.values(selectedCards)
      .flat()
      .find((c) => c.id === card.id);
    if (isAlreadySelected || current.length >= max) return;

    setSelectedCards({
      ...selectedCards,
      [roleKey]: [...current, card],
    });
  };

  const handleRemove = (roleKey, card) => {
    setSelectedCards({
      ...selectedCards,
      [roleKey]: selectedCards[roleKey].filter((c) => c.id !== card.id),
    });
  };

  const isCardSelected = (card) => {
    return Object.values(selectedCards)
      .flat()
      .find((c) => c.id === card.id);
  };

  const isDeckComplete = () => {
    return Object.keys(ROLE_REQUIREMENTS).every(
      (role) => selectedCards[role].length === ROLE_REQUIREMENTS[role],
    );
  };

  const randomFillDeck = () => {
    // Shuffle cards and pick 6
    const shuffled = [...ALL_CARDS].sort(() => Math.random() - 0.5);
    let cardIndex = 0;

    const newDeck = {
      facilitator: [],
      critic: [],
      stateTracker: [],
      reasoner: [],
    };

    // Fill each role with required number of cards
    for (const [role, required] of Object.entries(ROLE_REQUIREMENTS)) {
      for (let i = 0; i < required; i++) {
        if (cardIndex < shuffled.length) {
          newDeck[role].push(shuffled[cardIndex]);
          cardIndex++;
        }
      }
    }

    setSelectedCards(newDeck);
  };

  const handleStartGame = async () => {
    if (!isDeckComplete()) return;

    // Build agents array with model, expertise, personality, role
    const agents = [];
    for (const [role, cards] of Object.entries(selectedCards)) {
      for (const card of cards) {
        agents.push({
          model: card.model,
          expertise: card.expertise,
          personality: card.personality,
          role: role,
        });
      }
    }

    console.log("Submitting deck:", JSON.stringify({ agents }, null, 2));

    try {
      const response = await fetch("/api/deck", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ agents }),
      });

      if (!response.ok) throw new Error("Failed to submit deck");

      navigate("/game");
    } catch (err) {
      console.error("Error submitting deck:", err);
    }
  };

  return (
    <div className="min-h-screen bg-neutral-950 text-white p-8 pb-44">
      <div className="max-w-6xl mx-auto">
        <div className="mb-8 text-center">
          <h1 className="text-4xl font-black tracking-tight mb-2">
            Pick Your Team
          </h1>
          <p className="text-neutral-500">Drag 6 agents to your deck below</p>
        </div>

        {/* Card Pool */}
        <div className="flex flex-wrap gap-10 justify-center">
          {ALL_CARDS.map((card) => (
            <Card
              key={card.id}
              id={card.id}
              model={card.model}
              expertise={card.expertise}
              personality={card.personality}
              selected={!!isCardSelected(card)}
            />
          ))}
        </div>
      </div>

      {/* Selected Deck - Bottom Bar */}
      <div
        className={`fixed bottom-0 left-0 right-0 bg-neutral-900 border-t-2 border-amber-500/80 transition-transform duration-300 ${isCollapsed ? "translate-y-[calc(100%-3rem)]" : ""}`}
      >
        {/* Toggle Button */}
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="absolute -top-8 left-1/2 -translate-x-1/2 bg-neutral-900 border-2 border-b-0 border-amber-500/80 rounded-t-lg px-4 py-1 text-neutral-400 hover:text-white transition-colors"
        >
          <span
            className={`inline-block transition-transform ${isCollapsed ? "rotate-180" : ""}`}
          >
            ▼
          </span>
          <span className="ml-2 text-sm font-medium">
            {Object.values(selectedCards).flat().length}/6
          </span>
        </button>

        <div className="py-5 px-8">
          <div className="flex items-center justify-between gap-8">
            <div className="flex gap-8 flex-1">
              {Object.entries(ROLE_REQUIREMENTS).map(([role, required]) => (
                <RoleSlot
                  key={role}
                  role={role.replace(/([A-Z])/g, " $1").trim()}
                  roleKey={role}
                  required={required}
                  selected={selectedCards[role]}
                  onDrop={(card) => handleDrop(role, card)}
                  onRemove={(card) => handleRemove(role, card)}
                />
              ))}
            </div>

            <div className="flex items-center gap-3 shrink-0">
              <button
                onClick={randomFillDeck}
                className="px-4 py-2 text-sm text-amber-400 hover:text-amber-300 transition-colors font-medium"
              >
                Random Fill
              </button>
              <button
                onClick={() =>
                  setSelectedCards({
                    facilitator: [],
                    critic: [],
                    stateTracker: [],
                    reasoner: [],
                  })
                }
                className="px-4 py-2 text-sm text-neutral-400 hover:text-white transition-colors font-medium"
              >
                Clear All
              </button>
              <Button
                onClick={handleStartGame}
                className={`${!isDeckComplete() ? "opacity-50 cursor-not-allowed" : ""}`}
              >
                {isDeckComplete()
                  ? "Start Game"
                  : `${6 - Object.values(selectedCards).flat().length} more`}
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CardSelect;
