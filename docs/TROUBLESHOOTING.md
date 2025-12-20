# Troubleshooting Guide

## Docker Permission Issues

If you get `permission denied while trying to connect to the docker API`, you have a few options:

### Option 1: Add user to docker group (Recommended)

```bash
sudo usermod -aG docker $USER
newgrp docker
```

Then try again:
```bash
docker compose ps
```

### Option 2: Use sudo (Not recommended for long-term use)

```bash
sudo docker compose up
```

### Option 3: Check if Docker daemon is running

```bash
sudo systemctl status docker
# If not running:
sudo systemctl start docker
```

## Backend Not Responding (ERR_EMPTY_RESPONSE)

### Check if services are running

```bash
docker compose ps
# or
docker ps
```

### Start the services

```bash
docker compose up -d
```

### View backend logs

```bash
docker compose logs backend -f
```

### Common issues:

1. **Backend not starting**: Check logs for Python errors
2. **Port already in use**: Another service might be using port 8001
3. **SurrealDB not ready**: Backend depends on SurrealDB, check if it's running

### Check if backend is accessible

```bash
curl http://localhost:8001/api/health
```

Should return: `{"status":"ok"}`

## Frontend Can't Connect to Backend

### Check environment variable

The frontend uses `VITE_API_URL` environment variable. Make sure it's set correctly in `docker-compose.yml`:

```yaml
environment:
  - REACT_APP_API_URL=http://localhost:8001
```

Note: If running frontend outside Docker, use `http://localhost:8001`. If running inside Docker, it should use the service name.

### Rebuild frontend after env change

```bash
docker compose up --build frontend
```

## Reset Everything

If you want to start fresh:

```bash
# Stop all services
docker compose down

# Remove volumes (this will delete database data)
docker compose down -v

# Rebuild and start
docker compose up --build
```

