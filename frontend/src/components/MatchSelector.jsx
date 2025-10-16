import React, { useState, useEffect } from 'react'
import { getUpcomingMatches } from '../api'
import './MatchSelector.css'

export default function MatchSelector({ onSelectMatch, selectedMatch }){
  const [matches, setMatches] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [selectedLeague, setSelectedLeague] = useState('ALL')

  useEffect(() => {
    let cancelled = false
    
    async function loadMatches(){
      setLoading(true)
      setError('')
      setMatches([]) // Clear old matches immediately
      
      try{
        console.log('Fetching matches for league:', selectedLeague)
        const data = await getUpcomingMatches(selectedLeague, 14)
        console.log('Received data:', data)
        console.log('Matches count:', data.matches?.length)
        
        if(!cancelled) {
          setMatches(data.matches || [])
          if(!data.matches || data.matches.length === 0) {
            setError('No upcoming matches in the next 14 days')
          }
        }
      }catch(err){
        console.error('Error loading matches:', err)
        if(!cancelled) {
          setError('Unable to load matches. Make sure the backend is running.')
        }
      }finally{
        if(!cancelled) {
          setLoading(false)
        }
      }
    }
    
    loadMatches()
    
    return () => {
      cancelled = true
    }
  }, [selectedLeague])

  const leagues = [
    { code: 'ALL', name: 'All Leagues', display: 'ALL' },
    { code: 'PL', name: 'Premier League', display: 'ENG' },
    { code: 'PD', name: 'La Liga', display: 'ESP' },
    { code: 'BL1', name: 'Bundesliga', display: 'GER' },
    { code: 'SA', name: 'Serie A', display: 'ITA' },
    { code: 'FL1', name: 'Ligue 1', display: 'FRA' }
  ]

  return (
    <div className="match-selector">
      <div className="selector-header">
        <h3>Upcoming Matches</h3>
        <div className="league-selector">
          {leagues.map(league => (
            <button
              key={league.code}
              className={`league-btn ${selectedLeague === league.code ? 'active' : ''}`}
              onClick={() => setSelectedLeague(league.code)}
              title={league.name}
            >
              {league.display}
            </button>
          ))}
        </div>
      </div>
      {loading && <div className="loading">Loading matches from API...</div>}
      {error && <div className="error">{error}</div>}
      <div className="match-list">
        {matches.map(m => (
          <div 
            key={m.id} 
            className={`match-card ${selectedMatch?.id === m.id ? 'selected' : ''}`}
            onClick={() => onSelectMatch(m)}
          >
            <div className="teams">
              <span>{m.home_team}</span>
              <span className="vs">vs</span>
              <span>{m.away_team}</span>
            </div>
            <div className="meta">
              {new Date(m.date).toLocaleDateString('en-US', { 
                month: 'short', 
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
              })}
              <span>•</span>
              <span>{m.competition}</span>
            </div>
            {m.odds && (
              <div className="odds">
                <div className="odd-item">H: {m.odds.Home || m.odds['1'] || 'N/A'}</div>
                <div className="odd-item">D: {m.odds.Draw || m.odds['X'] || 'N/A'}</div>
                <div className="odd-item">A: {m.odds.Away || m.odds['2'] || 'N/A'}</div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
