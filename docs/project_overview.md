# CineBrain - Project Overview

## Problem Statement

Modern streaming applications (Netflix, Disney+, HBO Max) rely on recommendation systems that suggest movies similar to those a user has already watched or liked. Traditionally, such data is stored in relational databases, but they have limitations:

- Difficulties in flexible modeling of relationships (e.g., users – movies – genres)
- Challenges with fast queries like "show me users with similar preferences"

SurrealDB provides an interesting alternative because it:
- Combines features of relational, document, and graph databases
- Allows storing data in JSON format
- Supports relationships and graph queries (RELATE, FETCH)

## Solution

CineBrain is a web application that analyzes user preferences (ratings, genres, directors) and recommends movies similar to those they've already liked. The system is based on SurrealDB, a modern hybrid database (graph + document) that allows connecting users, movies, and genres in a relational structure without a rigid schema.

## Key Features

### Hybrid Data Model
SurrealDB serves as a flexible hybrid database in this project:
- Allows storing document data (JSON)
- Enables connecting records with relationships (RELATE)
- Provides a SQL-like query language with graph capabilities
- Features a schemaless mechanism, so data can be extended without table migrations

### Recommendation System
The application implements two types of recommendations:

1. **Similar Movies**: Based on genres of movies the user has rated
   ```sql
   SELECT ->rated->movie->belongs_to-><-belongs_to<-movie
   FROM user:oskar
   FETCH ->rated->movie->belongs_to;
   ```

2. **Similar Users**: Movies liked by users who rated the same movies
   ```sql
   SELECT <-rated<-user->rated->movie
   FROM movie:inception
   FETCH <-rated<-user->rated->movie;
   ```

## Architecture

- **Database**: SurrealDB (hybrid graph + document)
- **Backend**: FastAPI (Python)
- **Frontend**: React with Vite
- **Containerization**: Docker Compose

## Data Model

### Tables
- `user`: User information (name, email, age)
- `movie`: Movie information (title, year, director)
- `genre`: Genre categories
- `rating`: Relationship between users and movies (with score)

### Relationships
- `user->rated->movie`: User rates a movie with a score
- `movie->belongs_to->genre`: Movie belongs to one or more genres

## Advantages of SurrealDB Approach

1. **Flexibility**: No need for schema migrations when adding new fields
2. **Natural Relationships**: RELATE statements create graph connections naturally
3. **Query Power**: Graph queries allow traversing multiple relationship levels
4. **JSON Support**: Native JSON storage and querying
5. **Single Database**: Combines features of document and graph databases

## Comparison with Traditional Approaches

### vs. Relational Databases (PostgreSQL)
- **SurrealDB**: Flexible schema, natural graph queries
- **PostgreSQL**: Requires JOINs across multiple tables, rigid schema

### vs. Document Databases (MongoDB)
- **SurrealDB**: Native relationship support with RELATE
- **MongoDB**: Relationships require manual reference management

### vs. Graph Databases (Neo4j)
- **SurrealDB**: Document storage + graph capabilities
- **Neo4j**: Pure graph model, no document storage

## Use Cases

This approach is ideal for:
- Rapid prototyping of recommendation systems
- Applications requiring both document and graph features
- Systems needing flexible data models
- Projects where schema evolution is frequent

