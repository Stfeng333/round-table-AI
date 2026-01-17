import React from 'react'
import { useNavigate } from 'react-router-dom'
import Button from '../components/common/Button'

const Welcome = () => {
  const navigate = useNavigate()

  const handleStartGame = () => {
    navigate('/game')
  }

  return (
    <div 
      className="w-screen h-screen flex flex-row items-center justify-center bg-cover bg-center bg-no-repeat"
      style={{ backgroundImage: "url('/background.png')" }}
    >
      <div className="text-center bg-black/50 backdrop-blur-sm p-12 rounded-2xl">
        <h1 className="text-6xl font-bold text-white mb-4 drop-shadow-lg">
          Agent Arena
        </h1>
        <p className="text-xl text-gray-100 mb-12 drop-shadow-md">
          Assemble your team of LLM agents to solve the challenge
        </p>
        <Button onClick={handleStartGame}>
          Start Game
        </Button>
      </div>
    </div>
  )
}

export default Welcome