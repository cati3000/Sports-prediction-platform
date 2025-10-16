import React from 'react'
import './ParlayBuilder.css'

function combined(legs){
  if (legs.length === 0) return { combOdds: 0, combProb: 0, payout: 0 }
  let combOdds = 1
  let combProb = 1
  for(const l of legs){ combOdds *= l.odds; combProb *= l.prob }
  return { combOdds: combOdds.toFixed(2), combProb: (combProb * 100).toFixed(2), payout: (combOdds * 10).toFixed(2) }
}

export default function ParlayBuilder({ legs, onRemove }){
  const s = combined(legs)
  
  return (
    <div className="parlay">
      <h3>Your Parlay</h3>
      {legs.length === 0 && <div className="empty">Add events from predictions to build your parlay</div>}
      
      {legs.map((l, i)=> (
        <div key={i} className="leg">
          <div className="leg-info">
            <div className="event">{l.event}</div>
            <div className="meta">
              <span>Prob: {(l.prob * 100).toFixed(1)}%</span>
              <span>Odds: {l.odds}</span>
              <span className={l.ev > 0 ? 'positive' : ''}>
                EV: {(l.ev * 100).toFixed(1)}%
              </span>
            </div>
          </div>
          <button className="btn remove" onClick={()=>onRemove(i)}>
            Remove
          </button>
        </div>
      ))}

      {legs.length > 0 && (
        <>
          <div className="summary">
            <div className="summary-row">
              <span className="label">Total Legs</span>
              <span className="value">{legs.length}</span>
            </div>
            <div className="summary-row">
              <span className="label">Combined Odds</span>
              <span className="value">{s.combOdds}x</span>
            </div>
            <div className="summary-row">
              <span className="label">Win Probability</span>
              <span className="value">{s.combProb}%</span>
            </div>
            <div className="summary-row highlight">
              <span className="label">Potential Win ($10)</span>
              <span className="value">${s.payout}</span>
            </div>
          </div>
          <button className="place-bet-btn">
            Place Parlay Bet
          </button>
        </>
      )}
    </div>
  )
}
