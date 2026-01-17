import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import Card from "../components/CardSelect/Card";
import RoleSlot from "../components/CardSelect/RoleSlot";
import Button from "../components/common/Button";

const GOOD_TRAITS = [
  "Optimalist",
  "Aggressor",
  "Defender",
  "Gambler",
  "Exploitative",
  "Bluffer",
  "Truthful",
  "Adaptive",
  "Tilt-Prone",
  "Short-Memory",
  "Archivist",
  "Pattern Hunter",
  "Rules Lawyer",
  "Tempo Breaker",
  "Staller",
  "Randomized",
  "Contrarian",
  "Saboteur",
  "Opportunist",
  "Punisher",
  "Snowballer",
  "Comeback Artist",
  "Greedy Optimizer",
  "Risk-Minimizer",
  "Meta Chaser",
  "Anti-Meta",
  "Predictable",
  "Deceptive",
  "Chaos Agent",
  "Endgame Specialist",
];

const BAD_TRAITS = [
  "Gambler",
  "Bluffer",
  "Truthful",
  "Tilt-Prone",
  "Short-Memory",
  "Predictable",
  "Randomized",
  "Over-Aggressor",
  "Over-Defender",
  "Chaos Agent",
  "Saboteur",
  "Tunnel Vision",
  "Panic Resetter",
  "Impatient Finisher",
  "Win-More Addict",
  "Slow Starter",
  "Overfitter",
  "Greedy Hoarder",
  "Hesitant Executor",
  "Delay Addict",
  "Information Hoarder",
  "Desperation Agent",
  "Lagging Mimic",
  "Full RNG Agent",
  "Premature Executor",
  "Resource Waster",
  "Condition Misreader",
  "Trap-Fixated",
  "Short-Term Thinker",
  "Forgetful Executor",
];

// Seeded random for consistent traits per card
const seededRandom = (seed) => {
  const x = Math.sin(seed) * 10000;
  return x - Math.floor(x);
};

const getRandomTraits = (cardId) => {
  const seed = parseInt(cardId) * 137;
  const goodIndex = Math.floor(seededRandom(seed) * GOOD_TRAITS.length);
  let badIndex = Math.floor(seededRandom(seed + 1) * BAD_TRAITS.length);

  // Ensure traits are different (in case lists overlap)
  if (GOOD_TRAITS[goodIndex] === BAD_TRAITS[badIndex]) {
    badIndex = (badIndex + 1) % BAD_TRAITS.length;
  }

  return {
    good: GOOD_TRAITS[goodIndex],
    bad: BAD_TRAITS[badIndex],
  };
};

// Placeholder cards - replace with real data later
const ALL_CARDS = [
  { id: "1", name: "Agent Alpha", ...getRandomTraits("1") },
  { id: "2", name: "Agent Beta", ...getRandomTraits("2") },
  { id: "3", name: "Agent Gamma", ...getRandomTraits("3") },
  { id: "4", name: "Agent Delta", ...getRandomTraits("4") },
  { id: "5", name: "Agent Epsilon", ...getRandomTraits("5") },
  { id: "6", name: "Agent Zeta", ...getRandomTraits("6") },
  { id: "7", name: "Agent Eta", ...getRandomTraits("7") },
  { id: "8", name: "Agent Theta", ...getRandomTraits("8") },
  { id: "9", name: "Agent Iota", ...getRandomTraits("9") },
  { id: "10", name: "Agent Kappa", ...getRandomTraits("10") },
  { id: "11", name: "Agent Lambda", ...getRandomTraits("11") },
  { id: "12", name: "Agent Mu", ...getRandomTraits("12") },
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

  const handleStartGame = async () => {
    if (!isDeckComplete()) return;

    // Build agents array with model, good, bad, role
    const agents = [];
    for (const [role, cards] of Object.entries(selectedCards)) {
      for (const card of cards) {
        agents.push({
          model: card.name,
          good_personality: card.good,
          bad_personality: card.bad,
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

      const data = await response.json();
      navigate("/game", { state: { deck: selectedCards, gameData: data } });
    } catch (err) {
      console.error("Error submitting deck:", err);
    }
  };

  return (
    <div className="min-h-screen bg-neutral-950 text-white p-8 pb-44">
      <div className="mb-8">
        <h1 className="text-4xl font-black tracking-tight mb-2">
          Pick Your Team
        </h1>
        <p className="text-neutral-500">Drag 6 agents to your deck below</p>
      </div>

      {/* Card Pool */}
      <div className="flex flex-wrap gap-5">
        {ALL_CARDS.map((card) => (
          <Card
            key={card.id}
            id={card.id}
            name={card.name}
            good={card.good}
            bad={card.bad}
            selected={!!isCardSelected(card)}
          />
        ))}
      </div>

      {/* Selected Deck - Bottom Bar */}
      <div className="fixed bottom-0 left-0 right-0 bg-neutral-900 border-t-2 border-amber-500/80 py-5 px-8">
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
  );
};

export default CardSelect;
