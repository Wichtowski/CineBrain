import asyncio
import os
from pathlib import Path
from surreal_client import SurrealClient

async def load_fixtures() -> None:
    surreal_url = os.getenv("SURREAL_URL", "http://surrealdb:8000")
    surreal_user = os.getenv("SURREAL_USER", "root")
    surreal_pass = os.getenv("SURREAL_PASS", "root")
    surreal_ns = os.getenv("SURREAL_NS", "test")
    surreal_db = os.getenv("SURREAL_DB", "test")
    
    client = SurrealClient(
        url=surreal_url,
        user=surreal_user,
        password=surreal_pass,
        namespace=surreal_ns,
        database=surreal_db
    )
    
    try:
        await client.connect()
        
        fixtures_path = Path(__file__).parent.parent / "db" / "fixtures.surql"
        
        if not fixtures_path.exists():
            print(f"Fixtures file not found at {fixtures_path}")
            return
        
        with open(fixtures_path, "r", encoding="utf-8") as f:
            fixtures_sql = f.read()
        
        queries = [q.strip() for q in fixtures_sql.split(";") if q.strip()]
        
        print(f"Loading {len(queries)} fixture statements...")
        
        for i, query in enumerate(queries, 1):
            if query:
                try:
                    await client.query(query + ";")
                    if i % 10 == 0:
                        print(f"Processed {i}/{len(queries)} statements...")
                except Exception as e:
                    print(f"Error executing query {i}: {e}")
                    print(f"Query: {query[:100]}...")
        
        print("Fixtures loaded successfully!")
        
    except Exception as e:
        print(f"Error loading fixtures: {e}")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(load_fixtures())

