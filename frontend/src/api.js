import axios from 'axios'

const client = axios.create({ 
  baseURL: 'http://localhost:8000',
  timeout: 30000  // 30 seconds for first load when cache is empty
})

export async function getUpcomingMatches(league = 'ALL', days = 14){
  console.log(`[API] Requesting matches - league: ${league}, days: ${days}`)
  try {
    const resp = await client.get('/matches', { params: { league, days } })
    console.log(`[API] Response status: ${resp.status}`)
    console.log(`[API] Response data:`, resp.data)
    return resp.data
  } catch (error) {
    console.error('[API] Error:', error.message)
    if (error.response) {
      console.error('[API] Response status:', error.response.status)
      console.error('[API] Response data:', error.response.data)
    }
    throw error
  }
}

export async function predict(matchId, home, away, context = {}){
  const resp = await client.post('/predict', { match_id: matchId, home_team: home, away_team: away, context })
  return resp.data
}
