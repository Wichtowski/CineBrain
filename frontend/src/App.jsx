import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Link, useNavigate } from 'react-router-dom'
import { api } from './api/client'
import { ToastProvider, useToast } from './components/Toast'
import './App.css'

const Login = () => {
  const [email, setEmail] = useState('oskar@example.com')
  const [password, setPassword] = useState('password123')
  const [isRegister, setIsRegister] = useState(false)
  const [name, setName] = useState('')
  const navigate = useNavigate()
  const { showToast } = useToast()

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!email || !password) {
      showToast('Please fill in all fields', 'error')
      return
    }
    try {
      const endpoint = isRegister ? '/api/auth/register' : '/api/auth/login'
      const data = isRegister ? { name, email, password } : { email, password }
      const response = await api.post(endpoint, data)
      localStorage.setItem('token', response.data.token)
      if (response.data.user) {
        localStorage.setItem('user', JSON.stringify(response.data.user))
      }
      showToast('Authentication successful!', 'success')
      navigate('/movies')
    } catch (error) {
      showToast(error.response?.data?.detail || 'Authentication failed', 'error')
    }
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2>{isRegister ? 'Register' : 'Login'}</h2>
        <form onSubmit={handleSubmit}>
          {isRegister && (
            <input
              type="text"
              placeholder="Name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          )}
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <button type="submit">{isRegister ? 'Register' : 'Login'}</button>
        </form>
        <p onClick={() => setIsRegister(!isRegister)} className="toggle-auth">
          {isRegister ? 'Already have an account? Login' : "Don't have an account? Register"}
        </p>
      </div>
    </div>
  )
}

const Movies = () => {
  const [allMovies, setAllMovies] = useState([])
  const [ratedMovies, setRatedMovies] = useState([])
  const [recommendations, setRecommendations] = useState([])
  const [loading, setLoading] = useState(true)
  const [userRatings, setUserRatings] = useState({})
  const [user, setUser] = useState(null)
  const [allMoviesExpanded, setAllMoviesExpanded] = useState(false)
  const [recommendationsExpanded, setRecommendationsExpanded] = useState(true)

  useEffect(() => {
    loadUserInfo()
    loadAllMovies()
    loadRatedMovies()
    loadRecommendations()
    loadUserRatings()
  }, [])

  const loadUserInfo = async () => {
    const storedUser = localStorage.getItem('user')
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser))
      } catch (e) {
        console.error('Failed to parse stored user:', e)
      }
    }
    
    try {
      const response = await api.get('/api/auth/me')
      setUser(response.data)
      localStorage.setItem('user', JSON.stringify(response.data))
    } catch (error) {
      console.error('Failed to load user info:', error)
    }
  }

  const loadUserRatings = async () => {
    try {
      const response = await api.get('/api/ratings/my-ratings')
      const ratingsMap = {}
      if (response.data && Array.isArray(response.data)) {
        response.data.forEach((rating) => {
          if (rating.movie_id) {
            const movieId = rating.movie_id.split(':')[1] || rating.movie_id
            ratingsMap[movieId] = rating.score
          }
        })
      }
      setUserRatings(ratingsMap)
    } catch (error) {
      console.error('Failed to load user ratings:', error)
    }
  }

  const loadAllMovies = async () => {
    try {
      const response = await api.get('/api/movies?all=true')
      setAllMovies(response.data || [])
    } catch (error) {
      console.error('Failed to load all movies:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadRatedMovies = async () => {
    try {
      const ratingsResponse = await api.get('/api/ratings/my-ratings')
      const movies = []
      if (ratingsResponse.data && Array.isArray(ratingsResponse.data)) {
        ratingsResponse.data.forEach((rating) => {
          if (rating.movie && typeof rating.movie === 'object') {
            movies.push(rating.movie)
          }
        })
      }
      setRatedMovies(movies)
    } catch (error) {
      console.error('Failed to load rated movies:', error)
    }
  }

  const loadRecommendations = async () => {
    try {
      const response = await api.get('/api/recommendations/similar-movies')
      setRecommendations(response.data || [])
    } catch (error) {
      console.error('Failed to load recommendations:', error)
    }
  }

  const handleRatingUpdate = () => {
    loadUserRatings()
    loadRatedMovies()
    loadRecommendations()
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    window.location.href = '/'
  }

  if (loading) return <div className="loading">Loading...</div>

  return (
    <div className="movies-container">
      <header className="header">
        <h1>CineBrain</h1>
        <div className="header-user-info">
          {user && (
            <span className="user-name">
              {user.name || user.email || 'User'}
            </span>
          )}
          <button onClick={handleLogout} className="logout-btn">Logout</button>
        </div>
      </header>
      
      <div className="content">
        <section className="accordion-section">
          <div className="accordion-header" onClick={() => setAllMoviesExpanded(!allMoviesExpanded)}>
            <h2>All Movies</h2>
            <span className="accordion-icon">{allMoviesExpanded ? '▼' : '▶'}</span>
          </div>
          {allMoviesExpanded && (
            <div className="accordion-content">
              <div className="movies-grid">
                {allMovies.length > 0 ? (
                  allMovies.map((movie) => (
                    <MovieCard key={movie.id} movie={movie} initialRating={userRatings[movie.id?.split(':')[1] || movie.id]} onRatingUpdate={handleRatingUpdate} />
                  ))
                ) : (
                  <p>No movies found.</p>
                )}
              </div>
            </div>
          )}
        </section>

        <section className="accordion-section">
          <div className="accordion-header" onClick={() => setRecommendationsExpanded(!recommendationsExpanded)}>
            <h2>Recommended for You</h2>
            <span className="accordion-icon">{recommendationsExpanded ? '▼' : '▶'}</span>
          </div>
          {recommendationsExpanded && (
            <div className="accordion-content">
              <div className="movies-grid">
                {recommendations.length > 0 ? (
                  recommendations.map((movie) => (
                    <MovieCard key={movie.id} movie={movie} initialRating={userRatings[movie.id?.split(':')[1] || movie.id]} onRatingUpdate={handleRatingUpdate} />
                  ))
                ) : (
                  <p>No recommendations yet. Rate some movies!</p>
                )}
              </div>
            </div>
          )}
        </section>

        <section className="rated-movies-section">
          <h2>Rated Movies</h2>
          <div className="movies-grid">
            {ratedMovies.length > 0 ? (
              ratedMovies.map((movie) => (
                <MovieCard key={movie.id} movie={movie} initialRating={userRatings[movie.id?.split(':')[1] || movie.id]} onRatingUpdate={handleRatingUpdate} />
              ))
            ) : (
              <p>You haven't rated any movies yet. Start rating to see them here!</p>
            )}
          </div>
        </section>
      </div>
    </div>
  )
}

const MovieCard = ({ movie, initialRating = 0, onRatingUpdate }) => {
  const [rating, setRating] = useState(initialRating || 0)
  const [submitting, setSubmitting] = useState(false)
  const { showToast } = useToast()

  useEffect(() => {
    setRating(initialRating || 0)
  }, [initialRating])

  const handleRate = async (score) => {
    setSubmitting(true)
    try {
      const movieId = movie.id.split(':')[1] || movie.id
      await api.post('/api/ratings', { movie_id: movieId, score })
      setRating(score)
      showToast('Rating submitted!', 'success')
      if (onRatingUpdate) {
        onRatingUpdate()
      }
    } catch (error) {
      showToast(error.response?.data?.detail || 'Failed to submit rating', 'error')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="movie-card">
      <h3>{movie.title}</h3>
      <p className="movie-year">{movie.year}</p>
      {movie.director && <p className="movie-director">Director: {movie.director}</p>}
      <div className="rating-section">
        <p>Rate this movie:</p>
        <div className="rating-buttons">
          {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((score) => (
            <button
              key={score}
              onClick={() => handleRate(score)}
              disabled={submitting}
              className={rating === score ? 'active' : ''}
            >
              {score}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}

const App = () => {
  return (
    <ToastProvider>
      <Router>
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/movies" element={<Movies />} />
        </Routes>
      </Router>
    </ToastProvider>
  )
}

export default App

