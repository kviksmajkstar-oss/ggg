import React, { useMemo, useState } from 'react'

const API = 'http://localhost:8000/api'

export function App() {
  const [query, setQuery] = useState('The Weeknd')
  const [username, setUsername] = useState('demo-user')
  const [tracks, setTracks] = useState([])
  const [rate, setRate] = useState(1)
  const [recommendations, setRecommendations] = useState([])

  const grouped = useMemo(() => {
    return tracks.reduce((acc, t) => {
      acc[t.provider] = acc[t.provider] || []
      acc[t.provider].push(t)
      return acc
    }, {})
  }, [tracks])

  const search = async () => {
    const r = await fetch(`${API}/search?query=${encodeURIComponent(query)}`)
    const data = await r.json()
    setTracks(data.tracks || [])
  }

  const sendInteraction = async (track, eventType) => {
    await fetch(`${API}/interaction`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, track, event_type: eventType, value: 1 }),
    })
  }

  const getRecommendations = async () => {
    const r = await fetch(`${API}/recommendations/${encodeURIComponent(username)}`)
    const data = await r.json()
    setRecommendations(data.tracks || [])
  }

  return (
    <div className="layout">
      <header>
        <h1>🎧 OneMusic AI</h1>
        <p>Spotify + SoundCloud + YouTube Music в одном приложении</p>
      </header>

      <section className="card controls">
        <input value={username} onChange={(e) => setUsername(e.target.value)} placeholder="username" />
        <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Искать музыку..." />
        <button onClick={search}>Поиск</button>
        <button onClick={getRecommendations}>AI рекомендации</button>
      </section>

      <section className="card">
        <h2>Slowed / Speed Up</h2>
        <label>Скорость: {rate.toFixed(2)}x</label>
        <input type="range" min="0.5" max="2" step="0.05" value={rate} onChange={(e) => setRate(Number(e.target.value))} />
      </section>

      <section className="grid">
        {Object.entries(grouped).map(([provider, list]) => (
          <div className="card" key={provider}>
            <h3>{provider}</h3>
            {list.map((t) => (
              <article key={`${t.provider}-${t.provider_track_id}`}>
                <strong>{t.title}</strong>
                <div>{t.artist}</div>
                <audio controls src={t.stream_url} playbackRate={rate} />
                <div className="row">
                  <button onClick={() => sendInteraction(t, 'play')}>Play</button>
                  <button onClick={() => sendInteraction(t, 'like')}>Like</button>
                  <button onClick={() => sendInteraction(t, 'save_offline')}>Offline</button>
                </div>
              </article>
            ))}
          </div>
        ))}
      </section>

      <section className="card">
        <h2>Рекомендации</h2>
        {recommendations.map((t) => (
          <div key={`${t.provider}-${t.provider_track_id}`}>{t.artist} — {t.title} ({t.genre})</div>
        ))}
      </section>
    </div>
  )
}
