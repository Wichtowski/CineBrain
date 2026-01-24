import React, { useEffect, useRef, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import * as d3 from 'd3'
import { api } from '../api/client'
import '../App.css'
import './GraphVisualization.css'

const GraphVisualization = () => {
  const svgRef = useRef(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [graphData, setGraphData] = useState(null)
  const [user, setUser] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    loadUserInfo()
    fetchGraphData()
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

  const fetchGraphData = async () => {
    try {
      setLoading(true)
      const response = await api.get('/api/graph/data')
      setGraphData(response.data)
      setError(null)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load graph data')
      console.error('Error fetching graph data:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (!graphData || !svgRef.current) return

    const svg = d3.select(svgRef.current)
    svg.selectAll('*').remove()

    const width = svgRef.current.clientWidth
    const height = svgRef.current.clientHeight

    const nodes = [
      ...graphData.users.map(user => ({
        id: user.id,
        name: user.name || user.email,
        type: 'user',
        ...user
      })),
      ...graphData.movies.map(movie => ({
        id: movie.id,
        name: movie.title,
        type: 'movie',
        ...movie
      }))
    ]

    const links = graphData.ratings.map(rating => ({
      source: rating.source,
      target: rating.target,
      score: rating.score
    }))

    const simulation = d3.forceSimulation(nodes)
      .force('link', d3.forceLink(links).id(d => d.id).distance(150))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(40))

    const g = svg.append('g')

    const zoom = d3.zoom()
      .scaleExtent([0.1, 4])
      .on('zoom', (event) => {
        g.attr('transform', event.transform)
      })

    svg.call(zoom)

    const link = g.append('g')
      .selectAll('line')
      .data(links)
      .join('line')
      .attr('class', 'link')
      .attr('stroke-width', d => Math.sqrt(d.score))

    const linkLabels = g.append('g')
      .selectAll('text')
      .data(links)
      .join('text')
      .attr('class', 'link-label')
      .text(d => d.score)

    const node = g.append('g')
      .selectAll('g')
      .data(nodes)
      .join('g')
      .attr('class', 'node')
      .call(d3.drag()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended))

    node.append('circle')
      .attr('r', d => d.type === 'user' ? 25 : 20)
      .attr('class', d => d.type)

    node.append('text')
      .attr('class', 'node-label')
      .attr('dy', d => d.type === 'user' ? -30 : -25)
      .text(d => d.name)

    node.append('title')
      .text(d => {
        if (d.type === 'user') {
          return `${d.name}\n${d.email}`
        } else {
          return `${d.name}\n${d.year || ''} ${d.director ? `\nDirector: ${d.director}` : ''}`
        }
      })

    simulation.on('tick', () => {
      link
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y)

      linkLabels
        .attr('x', d => (d.source.x + d.target.x) / 2)
        .attr('y', d => (d.source.y + d.target.y) / 2)

      node.attr('transform', d => `translate(${d.x},${d.y})`)
    })

    function dragstarted(event) {
      if (!event.active) simulation.alphaTarget(0.3).restart()
      event.subject.fx = event.subject.x
      event.subject.fy = event.subject.y
    }

    function dragged(event) {
      event.subject.fx = event.x
      event.subject.fy = event.y
    }

    function dragended(event) {
      if (!event.active) simulation.alphaTarget(0)
      event.subject.fx = null
      event.subject.fy = null
    }

    return () => {
      simulation.stop()
    }
  }, [graphData])

  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    navigate('/')
  }

  if (loading) {
    return (
      <div className="graph-page">
        <header className="header">
          <h1>CineBrain</h1>
          <nav className="header-nav">
            <Link to="/movies" className="nav-link">Movies</Link>
            <Link to="/graph" className="nav-link">Graph View</Link>
          </nav>
          <div className="header-user-info">
            {user && (
              <span className="user-name">
                {user.name || user.email || 'User'}
              </span>
            )}
            <button onClick={handleLogout} className="logout-btn">Logout</button>
          </div>
        </header>
        <div className="graph-loading">Loading graph data...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="graph-page">
        <header className="header">
          <h1>CineBrain</h1>
          <nav className="header-nav">
            <Link to="/movies" className="nav-link">Movies</Link>
            <Link to="/graph" className="nav-link">Graph View</Link>
          </nav>
          <div className="header-user-info">
            {user && (
              <span className="user-name">
                {user.name || user.email || 'User'}
              </span>
            )}
            <button onClick={handleLogout} className="logout-btn">Logout</button>
          </div>
        </header>
        <div className="graph-error">Error: {error}</div>
      </div>
    )
  }

  return (
    <div className="graph-page">
      <header className="header">
        <h1>CineBrain</h1>
        <nav className="header-nav">
          <Link to="/movies" className="nav-link">Movies</Link>
          <Link to="/graph" className="nav-link">Graph View</Link>
        </nav>
        <div className="header-user-info">
          {user && (
            <span className="user-name">
              {user.name || user.email || 'User'}
            </span>
          )}
          <button onClick={handleLogout} className="logout-btn">Logout</button>
        </div>
      </header>
      <div className="graph-container">
        <div className="graph-header">
          <h2>User-Movie Connections Graph</h2>
          <div className="graph-legend">
            <div className="legend-item">
              <div className="legend-color user"></div>
              <span>Users</span>
            </div>
            <div className="legend-item">
              <div className="legend-color movie"></div>
              <span>Movies</span>
            </div>
            <div className="legend-item">
              <div className="legend-line"></div>
              <span>Ratings (thickness = score)</span>
            </div>
          </div>
        </div>
        <svg ref={svgRef} className="graph-svg"></svg>
        <div className="graph-instructions">
          <p>💡 Drag nodes to rearrange • Scroll to zoom • Hover for details</p>
        </div>
      </div>
    </div>
  )
}

export default GraphVisualization
