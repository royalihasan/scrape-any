import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import ScrapeComponent from './components/ScrapeComponent '
function App() {
  const [count, setCount] = useState(0)

  return (
    <>
     <ScrapeComponent />
    </>
  )
}

export default App
