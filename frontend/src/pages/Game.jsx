import React, { useState, useEffect, useRef } from "react";
import Button from "../components/common/Button";

// Simple markdown parser for **bold** text, strips <think> tags
const renderMarkdown = (text) => {
  if (!text) return text;
  // Remove <think>...</think> blocks (some models output reasoning)
  let cleaned = text.replace(/<think>[\s\S]*?<\/think>/gi, "").trim();
  const parts = cleaned.split(/(\*\*[^*]+\*\*)/g);
  return parts.map((part, i) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return <strong key={i}>{part.slice(2, -2)}</strong>;
    }
    return part;
  });
};

const PUZZLES = {
  "Math Problem": `What's 1 + 1?`,

  "Murder at Blackwood Manor": `The Fortress Blackwood Manor was a Victorian gargoyle of stone and rot. Inside, the air was a suffocating mix of lavender and the coppery tang of recent death. Beatrice Hemlock lay in the Yellow Drawing Room—a hermetically sealed tomb. The door was bolted from the inside; the windows were latched; the chimney was barred.

On the mahogany table sat cold Earl Grey and an open bottle of heart medication, its safety cap discarded on the rug like a spent shell casing. A single white pill rested at the table's extreme edge—perfectly dry. Beside it lay Beatrice's personal ledger. The morning's entries were sharp, but the final lines were a jagged, desperate scrawl of crossed-out dosages. In her arrogance, she had tried to map her own survival and lost her way.

The Vultures: The three heirs were a triad of golden rot, gathered in the music room:
- Julian: Nursed a crystal glass, complaining the police tape was an "aesthetic violation." He ignored his severe almond allergy, mindlessly reaching for a bowl of mixed nuts.
- Elara: Calculated the market value of the Ming vases while her mother's chalk outline still gripped the carpet.
- Sloane: Fretted over her Hamptons gala, treating the death as a "vibe-shift" she hadn't consented to.

The Shadow in the Kitchen: Mrs. Holloway, the heartbeat of the manor for twenty years, stood by the sideboard. She had been "retained" for the night because the heirs couldn't operate the industrial coffee machine. She moved with predatory grace, her eyes never leaving the back of Julian's neck.

As she poured Julian's coffee, her hand trembled—not with grief, but with a restrained, violent energy. The detective noticed a small, unlabeled vial of clear liquid tucked into her apron string.

"Master Julian always did have such... delicate requirements," she whispered, stirring his cup with a silver spoon. "He never could resist the sweetness of a specialized blend."

The Final Inventory: The detective looked from the jagged ledger in the drawing room to the special coffee in the dining hall.

Question: What happened to Beatrice, and what is about to happen to Julian?`,
};

const Game = () => {
  const [selectedOption, setSelectedOption] = useState("");
  const [puzzleText, setPuzzleText] = useState("");
  const [history, setHistory] = useState([]);
  const historyEndRef = useRef(null);

  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const response = await fetch("http://localhost:5000/api/sync");
        const data = await response.json();
        if (data.text) {
          setHistory((prev) => {
            if (prev[prev.length - 1]?.text !== data.text) {
              return [...prev, { text: data.text, colour: data.colour }];
            }
            return prev;
          });
        }
      } catch (error) {
        console.error("Sync error:", error);
      }
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    historyEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [history]);

  const handleSelectChange = (e) => {
    const selected = e.target.value;
    setSelectedOption(selected);
    setPuzzleText(PUZZLES[selected] || "");
  };

  const handleSubmit = async () => {
    if (!puzzleText) return;

    try {
      const response = await fetch("http://localhost:5000/api/puzzle", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ puzzle: puzzleText }),
      });

      if (!response.ok) throw new Error("Failed to submit puzzle");
      setSelectedOption("");
      setPuzzleText("");
    } catch (error) {
      console.error("Submit error:", error);
    }
  };

  return (
    <div className="h-screen bg-neutral-950 text-white p-8 flex flex-col overflow-hidden">
      <div className="flex gap-8 flex-1 min-h-0">
        {/* Left Panel */}
        <div className="flex-1 flex flex-col gap-4 min-h-0">
          <div className="flex gap-2">
            <select
              value={selectedOption}
              onChange={handleSelectChange}
              className="flex-1 bg-neutral-800 border border-neutral-700 text-white rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
            >
              <option value="">Choose a puzzle...</option>
              {Object.keys(PUZZLES).map((puzzle) => (
                <option key={puzzle} value={puzzle}>
                  {puzzle}
                </option>
              ))}
            </select>
            <Button onClick={handleSubmit} disabled={!puzzleText}>
              Submit
            </Button>
          </div>

          <div className="flex-1 bg-neutral-900 border border-neutral-700 rounded-lg p-6 overflow-y-auto min-h-0">
            <p className="text-neutral-200 leading-relaxed whitespace-pre-wrap">
              {puzzleText || (
                <span className="text-neutral-500">
                  Select a puzzle to view details...
                </span>
              )}
            </p>
          </div>
        </div>

        {/* Right Panel - History */}
        <div className="flex-1 flex flex-col min-h-0">
          <div className="flex-1 overflow-y-auto bg-neutral-900 border border-neutral-700 rounded-lg p-4 space-y-2 min-h-0">
            {history.length === 0 ? (
              <p className="text-neutral-500 text-sm">
                Waiting for activity...
              </p>
            ) : (
              history.map((item, idx) => (
                <div
                  key={idx}
                  className="text-sm text-neutral-300 bg-neutral-800 p-2 rounded"
                  style={{
                    borderLeftColor: item.colour,
                    borderLeftWidth: "4px",
                  }}
                >
                  {renderMarkdown(item.text)}
                </div>
              ))
            )}
            <div ref={historyEndRef} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Game;
