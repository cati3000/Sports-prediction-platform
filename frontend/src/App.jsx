import React, { useState } from 'react'
import MatchSelector from './components/MatchSelector'
import PredictionPanel from './components/PredictionPanel'
import ParlayBuilder from './components/ParlayBuilder'
import './app.css'

export default function App(){
  const [legs, setLegs] = useState([])
  const [selectedMatch, setSelectedMatch] = useState(null)

  function addLeg(l){
    // avoid duplicates
    if(legs.some(x=>x.event===l.event)) return
    setLegs([...legs, l])
  }

  function removeLeg(idx){
    const copy = legs.slice(); copy.splice(idx,1); setLegs(copy)
  }

  return (
    <div className="app-root">
      <header className="header">
        <h1>AI Parlay Predictor</h1>
        <div className="subtitle">Data-Driven Predictions • Real Odds • Smart Parlays</div>
      </header>
      <main className="main">
        <div className="left-col">
          <MatchSelector onSelectMatch={setSelectedMatch} selectedMatch={selectedMatch} />
          <PredictionPanel selectedMatch={selectedMatch} onAddLeg={addLeg} />
        </div>
        <aside className="right-col">
          <ParlayBuilder legs={legs} onRemove={removeLeg} />
        </aside>
      </main>
    </div>
  )
}
