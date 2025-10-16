import React, { useState, useEffect } from 'react'
import { predict } from '../api'
import './PredictionPanel.css'

export default function PredictionPanel({ selectedMatch, onAddLeg }){
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [expandedMarket, setExpandedMarket] = useState('match-result')

  useEffect(() => {
    if (selectedMatch) {
      onPredict()
    }
  }, [selectedMatch])

  async function onPredict(){
    if (!selectedMatch) {
      setError('Please select a match first')
      return
    }
    
    setLoading(true)
    setError('')
    try{
      const context = { 
        real_match_id: selectedMatch.id,
        odds_data: {
          home_odds: selectedMatch.odds?.Home || selectedMatch.odds?.['1'] || 2.0,
          away_odds: selectedMatch.odds?.Away || selectedMatch.odds?.['2'] || 3.0
        }
      }
      
      const data = await predict(
        String(selectedMatch.id), 
        selectedMatch.home_team, 
        selectedMatch.away_team, 
        context
      )
      setResults(data.candidates || [])
    }catch(err){
      console.error('Prediction error:', err)
      setResults([])
      setError('Failed to generate predictions. Check backend connection.')
    }finally{
      setLoading(false)
    }
  }

  if (!selectedMatch) {
    return (
      <div className="prediction-panel">
        <div className="select-prompt">
          Select a match to view betting markets and AI predictions
        </div>
      </div>
    )
  }

  // Group predictions by market type
  const markets = {
    'match-result': {
      title: 'Match Result',
      bets: results.filter(r => 
        r.event.includes('Win') || 
        r.event.includes('win') ||
        r.event.includes('Draw') ||
        r.event.toLowerCase().includes('draw')
      )
    },
    'goals': {
      title: 'Goals',
      bets: results.filter(r => 
        (r.event.toLowerCase().includes('goal') ||
        r.event.toLowerCase().includes('over') ||
        r.event.toLowerCase().includes('under')) &&
        !r.event.toLowerCase().includes('btts') &&
        !r.event.toLowerCase().includes('both teams')
      )
    },
    'btts': {
      title: 'Both Teams To Score',
      bets: results.filter(r => 
        r.event.toLowerCase().includes('btts') ||
        r.event.toLowerCase().includes('both teams')
      )
    },
    'corners': {
      title: 'Corners & Cards',
      bets: results.filter(r => 
        r.event.toLowerCase().includes('corner') ||
        r.event.toLowerCase().includes('card') ||
        r.event.toLowerCase().includes('booking')
      )
    }
  }

  return (
    <div className="prediction-panel">
      <div className="match-header">
        <div className="teams-display">
          <div className="team">{selectedMatch.home_team}</div>
          <div className="vs">VS</div>
          <div className="team">{selectedMatch.away_team}</div>
        </div>
        <div className="match-meta">
          {new Date(selectedMatch.date).toLocaleString('en-US', { 
            month: 'short', 
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
          })} • {selectedMatch.competition}
        </div>
      </div>

      {loading && (
        <div className="loading-state">
          <div className="spinner"></div>
          Analyzing match data...
        </div>
      )}

      {error && <div className="error-message">{error}</div>}

      {!loading && !error && results.length > 0 && (
        <div className="markets-container">
          {Object.entries(markets).map(([key, market]) => {
            if (market.bets.length === 0) return null
            const isExpanded = expandedMarket === key

            return (
              <div key={key} className={`market-section ${isExpanded ? 'expanded' : ''}`}>
                <div 
                  className="market-header"
                  onClick={() => setExpandedMarket(isExpanded ? null : key)}
                >
                  <div className="market-title">
                    <span>{market.title}</span>
                    <span className="bet-count">{market.bets.length}</span>
                  </div>
                  <div className="expand-icon">{isExpanded ? '−' : '+'}</div>
                </div>

                {isExpanded && (
                  <div className="market-content">
                    {market.bets.map((bet, idx) => {
                      const prob = (bet.prob * 100).toFixed(0)
                      const ev = bet.ev || 0
                      const isValue = ev > 0

                      return (
                        <div key={idx} className={`bet-row ${isValue ? 'value-bet' : ''}`}>
                          <div className="bet-info">
                            <div className="bet-name">{bet.event}</div>
                            {bet.reasoning && (
                              <div className="bet-reasoning">{bet.reasoning}</div>
                            )}
                            <div className="bet-stats">
                              <span className="prob">{prob}% probability</span>
                              <span className="ev-display">EV: {(ev * 100).toFixed(1)}%</span>
                              {isValue && <span className="value-tag">VALUE BET</span>}
                            </div>
                          </div>
                          <div className="bet-actions">
                            <div className="odds-display">{bet.odds?.toFixed(2) || 'N/A'}</div>
                            <button 
                              className="add-bet-btn"
                              onClick={() => onAddLeg(bet)}
                            >
                              Add
                            </button>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}

      {!loading && !error && results.length === 0 && (
        <div className="no-predictions">
          No predictions available for this match
        </div>
      )}
    </div>
  )
}
