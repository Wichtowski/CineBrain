# Graph Visualization Feature

## Overview
An interactive graph visualization that displays the connections between users, movies, and their ratings in the CineBrain application.

## Features

### Visual Elements
- **User Nodes**: Red circles representing users in the system
- **Movie Nodes**: Cyan/turquoise circles representing movies
- **Rating Edges**: Lines connecting users to movies they've rated
  - Line thickness represents the rating score (1-10)
  - Rating scores are displayed as labels on the connections

### Interactions
- **Drag**: Click and drag any node to reposition it in the graph
- **Zoom**: Use mouse wheel or trackpad to zoom in/out
- **Pan**: Click and drag on empty space to pan around the graph
- **Hover**: Hover over nodes to see detailed information
  - Users: Name and email
  - Movies: Title, year, and director

### Navigation
Access the graph view by clicking "Graph View" in the navigation menu after logging in.

## Technical Implementation

### Backend
- **Endpoint**: `GET /api/graph/data`
- **Returns**: JSON object containing:
  - `users`: Array of user objects (id, name, email)
  - `movies`: Array of movie objects (id, title, year, director)
  - `ratings`: Array of rating relationships (source, target, score)

### Frontend
- **Component**: `GraphVisualization.jsx`
- **Library**: D3.js (v7.x) for force-directed graph layout
- **Location**: `/graph` route
- **Styling**: Custom CSS with dark theme matching the app aesthetic

### Graph Layout
Uses D3's force simulation with:
- **Link force**: Maintains connections between nodes (distance: 150px)
- **Charge force**: Nodes repel each other (strength: -300)
- **Center force**: Keeps graph centered in viewport
- **Collision force**: Prevents node overlap (radius: 40px)

## Files Added/Modified

### New Files
- `/frontend/src/components/GraphVisualization.jsx` - Main graph component
- `/frontend/src/components/GraphVisualization.css` - Graph styling

### Modified Files
- `/backend/app.py` - Added `/api/graph/data` endpoint
- `/frontend/src/App.jsx` - Added graph route and navigation
- `/frontend/src/App.css` - Added navigation styling
- `/frontend/package.json` - Added D3.js dependency

## Usage

1. Log in to the application
2. Click "Graph View" in the header navigation
3. Explore the connections:
   - See which users rated which movies
   - View rating scores on the connection lines
   - Drag nodes to better visualize relationships
   - Zoom and pan for detailed exploration

## Future Enhancements
- Filter by rating score range
- Highlight specific users or movies
- Show genre connections
- Add clustering by movie similarity
- Export graph as image
- Time-based animation of ratings
