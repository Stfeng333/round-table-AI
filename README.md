# Round Table AI

**Choose your AI knights and solve the problem**

An interactive debate system where multiple AI models collaborate to solve puzzles and murder mysteries through structured discussion. Watch as different AI models with unique personalities and expertise debate for solutions.

## Features of our game
- **Multi-Model Debates**: Combine up to 6 AI models in a single debate
- **Role-Based Discussion**: Facilitator, Reasoner, Critic, and State Tracker roles
- **Real-Time Streaming**: Watch the debate unfold in real-time
- **Free Models Available**: Uses Groq's free API for most models

## Available AI models for free
| Model | Provider | Cost | Description |
|-------|----------|------|-------------|
| **ChatGPT** | Groq | **FREE** | Open-source GPT model (gpt-oss-120b) |
| **Llama** | Groq | **FREE** | Meta's Llama 3.3 70B |
| **Qwen** | Groq | **FREE** | Alibaba's Qwen 3 32B |
| **Kimi** | Groq | **FREE** | Moonshot AI's Kimi K2 (256k context) |
| **Gemini** | Google | Free tier available | Google's Gemini 2.5 Flash |

> **Note**: "ChatGPT" uses Groq's free open-source GPT model in our code, NOT OpenAI's paid API. You only need a free Groq API key

### Prerequisites
- **Python 3.8+** (tested on Python 3.14)
- **Node.js 16+** and npm
- **API Keys** (see setup below)

### 1. Get Your API Keys (FREE)
You'll need at least one of these free API keys:
- **Groq API** (recommended - powers 4 models): https://console.groq.com/keys
- **Google Gemini API**: https://aistudio.google.com/app/apikey

### 2. Clone and setup
```bash
# Clone the repository
git clone git@github.com:Stfeng333/round-table-AI.git
cd round-table-AI

# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### 3. Configure your environment
Create a `.env` file in the project root and follow our template:
```bash
GROQ_API_KEY=your_groq_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

### 4. Run the Application
**Terminal 1** - Start the backend:
```bash
python app_sam.py
```
**Terminal 2** - Start the frontend:
```bash
cd frontend
npm run dev
```
**Terminal 3** (Optional) - Run with Solace Agent Mesh:
```bash
sam run
```

### 5. Open Your Browser
Navigate to: **http://localhost:5173**

## Troubleshooting for you
**Issue**: "Error code: 429 - You exceeded your current quota"
- **Solution**: This means you're using OpenAI's paid API. Make sure you selected "ChatGPT" (which uses Groq) instead of creating an "OpenAI" model.

**Issue**: Backend not starting
- **Solution**: Make sure all dependencies are installed: `pip install -r requirements.txt`

**Issue**: Frontend shows "Waiting for activity..."
- **Solution**: Check that the backend is running on port 5000 and API keys are valid
