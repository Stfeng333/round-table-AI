"""
Debate Tools for Solace Agent Mesh
Provides dynamic LLM calling capabilities for OpenAI and Gemini models
to enable multi-model debate orchestration.
"""

import os
import json
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from google.adk.tools import ToolContext


# Role instructions for debate participants
ROLE_INSTRUCTIONS = {
    "critic": "Be critical and analytical of your teammates' contributions. Your goal is to achieve the team's objective of solving the puzzle by pushing your team to think of new ideas and challenging current ones.",
    "facilitator": "You are making the final decision - the solution that will solve the puzzle. That is your main focus. Listen to your teammates, but be decisive. VERY IMPORTANT: whenever you speak, end with one of the following: 'We need more discussion' or 'That is the answer.'. This is EXTREMELY important. Whatever you do, do not end with something other than this.",
    "reasoner": "Provide input on what you think the solution is. In all situations, contribute the most logical ideas that will help your team solve the puzzle.",
    "stateTracker": "Your job is not to reason, but to keep your teammates in check. Pay close attention to everything that's being discussed to make sure none of your teammates are fabricating facts. If that happens, remind them of the facts to guide them back on track."
}


def _build_system_prompt(role: str, personality: str, expertise: str) -> str:
    """Build the system prompt for a debate participant."""
    role_instruction = ROLE_INSTRUCTIONS.get(role, "Participate in the discussion constructively.")
    return f'''You are part of an elite reasoning team whose objective is to solve puzzles.
You will all take turns adding to the discussion. Work together to solve the problem. Once everyone has gone,
the facilitator will decide if there should be another round of discussion.
Your role is {role}. {role_instruction} Your personality is {personality}. Your expertise is {expertise}.
During discussion, act as someone with your personality and expertise would act. Be super concise in your speech. Try your best to go under 600 chars.
Everytime you speak, let everyone know your role in the following format : 'I am the <role>', where role is one of the following: state tracker, facilitator, reasoner, or critic. And remember, don't break character.
Follow the rules, work together, and support the facilitator until they can deliver the solution.
Before you are told to speak, you will be given the conversation that is currently unfolding. Don't hallucinate please.'''


def _call_openai(messages: List[Dict[str, str]], model: str = "gpt-4o") -> str:
    """Call OpenAI API with the given messages."""
    from openai import OpenAI
    
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return "Error: OPENAI_API_KEY not set in environment"
    
    client = OpenAI(api_key=api_key)
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=800,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"OpenAI Error: {str(e)}"


def _call_gemini(messages: List[Dict[str, str]], model: str = "gemini-2.0-flash") -> str:
    """Call Gemini API with the given messages."""
    from google import genai
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return "Error: GEMINI_API_KEY not set in environment"
    
    try:
        client = genai.Client(api_key=api_key)
        
        # Convert OpenAI-style messages to Gemini format
        # Extract system message and user messages
        system_content = ""
        conversation_parts = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_content = msg["content"]
            else:
                conversation_parts.append(msg["content"])
        
        # Combine system prompt with conversation
        full_prompt = system_content + "\n\n" + "\n".join(conversation_parts)
        
        response = client.models.generate_content(
            model=model,
            contents=full_prompt
        )
        return response.text
    except Exception as e:
        return f"Gemini Error: {str(e)}"


def call_llm(
    provider: str,
    role: str,
    personality: str,
    expertise: str,
    puzzle: str,
    conversation_history: str,
    prompt: str,
    model_name: Optional[str] = None,
    tool_context: Optional[ToolContext] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Call an LLM (OpenAI or Gemini) with debate participant configuration.
    
    Args:
        provider: The LLM provider to use ("openai" or "gemini")
        role: The debate role (facilitator, critic, reasoner, stateTracker)
        personality: The personality trait for this participant
        expertise: The area of expertise for this participant
        puzzle: The puzzle being debated
        conversation_history: Previous conversation in the debate
        prompt: The current prompt/instruction for the participant
        model_name: Optional specific model name to use
        
    Returns:
        Dict with status, response text, and metadata
    """
    provider = provider.lower().strip()
    
    # Build system prompt
    system_prompt = _build_system_prompt(role, personality, expertise)
    
    # Build messages
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"The puzzle is: {puzzle}"},
    ]
    
    # Add conversation history if present
    if conversation_history and conversation_history.strip():
        messages.append({"role": "user", "content": f"Conversation so far:\n{conversation_history}"})
    
    # Add current prompt
    messages.append({"role": "user", "content": prompt})
    
    # Call appropriate provider
    if provider == "openai" or provider == "chatgpt":
        model = model_name or "gpt-4o"
        response = _call_openai(messages, model)
    elif provider == "gemini":
        model = model_name or "gemini-2.0-flash"
        response = _call_gemini(messages, model)
    else:
        return {
            "status": "error",
            "message": f"Unknown provider: {provider}. Use 'openai' or 'gemini'.",
            "response": None
        }
    
    return {
        "status": "success",
        "provider": provider,
        "role": role,
        "personality": personality,
        "expertise": expertise,
        "response": response
    }


def run_debate(
    puzzle: str,
    cards: str,
    max_rounds: int = 4,
    tool_context: Optional[ToolContext] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Run a complete debate session with multiple LLM participants.
    
    Args:
        puzzle: The puzzle/problem to solve
        cards: JSON string of card configurations. Each card should have:
               - model: "openai" or "gemini" (or "ChatGPT" for openai)
               - role: "facilitator", "critic", "reasoner", or "stateTracker"
               - personality: Personality trait
               - expertise: Area of expertise
        max_rounds: Maximum number of debate rounds (default 4)
        
    Returns:
        Dict with debate history, final answer, and status
    """
    import random
    import time
    
    # Parse cards configuration
    try:
        if isinstance(cards, str):
            cards_list = json.loads(cards)
        else:
            cards_list = cards
    except json.JSONDecodeError as e:
        return {
            "status": "error",
            "message": f"Invalid cards JSON: {str(e)}",
            "debate_history": [],
            "final_answer": None
        }
    
    # Validate cards
    if not cards_list or len(cards_list) < 2:
        return {
            "status": "error",
            "message": "Need at least 2 cards to run a debate",
            "debate_history": [],
            "final_answer": None
        }
    
    # Find and separate facilitator
    facilitator = None
    participants = []
    
    for card in cards_list:
        if card.get("role", "").lower() == "facilitator":
            facilitator = card
        else:
            participants.append(card)
    
    if not facilitator:
        return {
            "status": "error",
            "message": "No facilitator found in cards. One card must have role='facilitator'",
            "debate_history": [],
            "final_answer": None
        }
    
    # Run debate
    debate_history = []
    conversation_text = ""
    final_answer = None
    
    for round_num in range(max_rounds):
        # Shuffle participants each round
        random.shuffle(participants)
        
        # Each participant speaks
        for card in participants:
            provider = card.get("model", "openai")
            # Map frontend model names to providers
            if provider.lower() in ["chatgpt", "gpt", "openai"]:
                provider = "openai"
            elif provider.lower() in ["gemini", "google"]:
                provider = "gemini"
            
            result = call_llm(
                provider=provider,
                role=card.get("role", "reasoner"),
                personality=card.get("personality", "analytical"),
                expertise=card.get("expertise", "general"),
                puzzle=puzzle,
                conversation_history=conversation_text,
                prompt="It is now your turn to speak."
            )
            
            if result["status"] == "success":
                response = result["response"]
                role = card.get("role", "unknown")
                
                # Add to history
                debate_history.append({
                    "role": role,
                    "model": card.get("model", "unknown"),
                    "personality": card.get("personality", ""),
                    "expertise": card.get("expertise", ""),
                    "message": response
                })
                
                # Update conversation text for context sharing
                conversation_text += f"\n[{role.upper()}]: {response}\n"
            else:
                debate_history.append({
                    "role": card.get("role", "unknown"),
                    "model": card.get("model", "unknown"),
                    "error": result.get("message", "Unknown error")
                })
            
            # Small delay to avoid rate limiting
            time.sleep(0.3)
        
        # Facilitator speaks
        fac_provider = facilitator.get("model", "openai")
        if fac_provider.lower() in ["chatgpt", "gpt", "openai"]:
            fac_provider = "openai"
        elif fac_provider.lower() in ["gemini", "google"]:
            fac_provider = "gemini"
        
        fac_result = call_llm(
            provider=fac_provider,
            role="facilitator",
            personality=facilitator.get("personality", "decisive"),
            expertise=facilitator.get("expertise", "leadership"),
            puzzle=puzzle,
            conversation_history=conversation_text,
            prompt="It is now your turn to speak."
        )
        
        if fac_result["status"] == "success":
            fac_response = fac_result["response"]
            
            debate_history.append({
                "role": "facilitator",
                "model": facilitator.get("model", "unknown"),
                "personality": facilitator.get("personality", ""),
                "expertise": facilitator.get("expertise", ""),
                "message": fac_response
            })
            
            conversation_text += f"\n[FACILITATOR]: {fac_response}\n"
            
            # Check if facilitator has reached a conclusion
            if "that is the answer" in fac_response.lower():
                final_answer = fac_response
                break
        else:
            debate_history.append({
                "role": "facilitator",
                "model": facilitator.get("model", "unknown"),
                "error": fac_result.get("message", "Unknown error")
            })
        
        time.sleep(0.3)
    
    return {
        "status": "completed",
        "rounds_completed": round_num + 1,
        "debate_history": debate_history,
        "final_answer": final_answer,
        "conversation_transcript": conversation_text
    }


def run_debate_streaming(
    puzzle: str,
    cards: list,
    max_rounds: int = 4,
    on_message: callable = None,
) -> Dict[str, Any]:
    """
    Run a debate with real-time message streaming via callback.
    
    Args:
        puzzle: The puzzle/problem to solve
        cards: List of card configurations (already parsed)
        max_rounds: Maximum number of debate rounds
        on_message: Callback function(role, message, model) called for each message
        
    Returns:
        Dict with status and final answer
    """
    import random
    import time
    
    cards_list = cards if isinstance(cards, list) else json.loads(cards)
    
    # Validate cards
    if not cards_list or len(cards_list) < 2:
        return {"status": "error", "message": "Need at least 2 cards"}
    
    # Find and separate facilitator
    facilitator = None
    participants = []
    
    for card in cards_list:
        if card.get("role", "").lower() == "facilitator":
            facilitator = card
        else:
            participants.append(card)
    
    if not facilitator:
        return {"status": "error", "message": "No facilitator found"}
    
    conversation_text = ""
    final_answer = None
    
    for round_num in range(max_rounds):
        random.shuffle(participants)
        
        # Each participant speaks
        for card in participants:
            provider = card.get("model", "openai")
            
            result = call_llm(
                provider=provider,
                role=card.get("role", "reasoner"),
                personality=card.get("personality", "analytical"),
                expertise=card.get("expertise", "general"),
                puzzle=puzzle,
                conversation_history=conversation_text,
                prompt="It is now your turn to speak."
            )
            
            if result["status"] == "success":
                response = result["response"]
                role = card.get("role", "unknown")
                model = card.get("model", "unknown")
                
                # Stream message immediately via callback
                if on_message:
                    on_message(role, response, model)
                
                conversation_text += f"\n[{role.upper()}]: {response}\n"
            else:
                if on_message:
                    on_message("error", result.get("message", "LLM Error"), card.get("model", "unknown"))
            
            time.sleep(0.3)
        
        # Facilitator speaks
        fac_result = call_llm(
            provider=facilitator.get("model", "openai"),
            role="facilitator",
            personality=facilitator.get("personality", "decisive"),
            expertise=facilitator.get("expertise", "leadership"),
            puzzle=puzzle,
            conversation_history=conversation_text,
            prompt="It is now your turn to speak."
        )
        
        if fac_result["status"] == "success":
            fac_response = fac_result["response"]
            
            # Stream facilitator message immediately
            if on_message:
                on_message("facilitator", fac_response, facilitator.get("model", "unknown"))
            
            conversation_text += f"\n[FACILITATOR]: {fac_response}\n"
            
            if "that is the answer" in fac_response.lower():
                final_answer = fac_response
                break
        else:
            if on_message:
                on_message("error", fac_result.get("message", "Facilitator Error"), facilitator.get("model", "unknown"))
        
        time.sleep(0.3)
    
    return {
        "status": "completed",
        "final_answer": final_answer
    }
