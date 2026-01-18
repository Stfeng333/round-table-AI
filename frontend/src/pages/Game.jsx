import React, { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import Button from "../components/common/Button";

const PUZZLES = {
  "Math Problem": `
    What's 1 + 1?`,
};

const Game = () => {
  const navigate = useNavigate();
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
                  {item.text}
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
