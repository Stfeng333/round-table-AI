import { Routes, Route } from 'react-router-dom'
import Welcome from './pages/Welcome'
import CardSelect from './pages/CardSelect'



function App() {
  return (
    <Routes>
      <Route path="/" element={<Welcome />} />
      <Route path="/CardSelection" element={<CardSelect />} />
    </Routes>
    
  )
}

export default App
