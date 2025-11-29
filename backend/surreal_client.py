import httpx
from typing import Any, Dict, List, Optional

class SurrealClient:
    def __init__(self, url: str = "http://localhost:8000", user: str = "root", password: str = "root", namespace: str = "test", database: str = "test"):
        self.url = url
        self.user = user
        self.password = password
        self.namespace = namespace
        self.database = database
        self.token: Optional[str] = None
        self.client = httpx.AsyncClient(timeout=30.0)

    async def connect(self) -> None:
        import base64
        
        try:
            test_url = f"{self.url}/health"
            test_response = await self.client.get(test_url, timeout=5.0)
            if test_response.status_code != 200:
                raise Exception(f"SurrealDB health check failed. Status: {test_response.status_code}")
            
            auth_string = f"{self.user}:{self.password}"
            auth_bytes = auth_string.encode('ascii')
            auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
            
            self.token = auth_b64
            print("Connected to SurrealDB using Basic Auth")
        except httpx.ConnectError as e:
            raise Exception(f"Cannot connect to SurrealDB at {self.url}. Is it running? {e}")
        except Exception as e:
            raise Exception(f"Error connecting to SurrealDB: {e}")

    async def query(self, query: str, variables: Optional[Dict[str, Any]] = None) -> List[Any]:
        if not self.token:
            await self.connect()
        
        url = f"{self.url}/sql"
        
        final_query = query
        if variables:
            for key, value in variables.items():
                if isinstance(value, str):
                    final_query = final_query.replace(f"${key}", f"'{value}'")
                else:
                    final_query = final_query.replace(f"${key}", str(value))
        
        use_statement = f"USE NS {self.namespace} DB {self.database}; "
        final_query = use_statement + final_query
        
        headers = {
            "Authorization": f"Basic {self.token}",
            "NS": self.namespace,
            "DB": self.database,
            "Content-Type": "text/plain",
            "Accept": "application/json"
        }
        
        print(f"Query: {final_query}")
        print(f"Headers: NS={self.namespace}, DB={self.database}")
        
        response = await self.client.post(url, content=final_query, headers=headers)
        
        print(f"Response status: {response.status_code}")
        
        response.raise_for_status()
        result = response.json()
        
        print(f"SurrealDB raw response: {result}")
        print(f"Response type: {type(result)}")
        
        if isinstance(result, list):
            parsed_results = []
            for item in result:
                if isinstance(item, dict):
                    if item.get("status") == "ERR":
                        error_msg = item.get("result", "Unknown error")
                        print(f"SurrealDB error: {error_msg}")
                        if "namespace" in error_msg.lower() or "database" in error_msg.lower():
                            raise Exception(f"SurrealDB configuration error: {error_msg}")
                        continue
                    if "result" in item:
                        res = item["result"]
                        if isinstance(res, list):
                            parsed_results.extend(res)
                        elif res is not None and not isinstance(res, str) or (isinstance(res, str) and not res.startswith("Specify")):
                            parsed_results.append(res)
                    elif "status" in item and item.get("status") == "OK":
                        if "result" in item:
                            res = item["result"]
                            if isinstance(res, list):
                                parsed_results.extend(res)
                            elif res is not None:
                                parsed_results.append(res)
                    else:
                        parsed_results.append(item)
                elif item is not None and not isinstance(item, str) or (isinstance(item, str) and not item.startswith("Specify")):
                    parsed_results.append(item)
            return parsed_results
        elif isinstance(result, dict):
            if result.get("status") == "ERR":
                error_msg = result.get("result", "Unknown error")
                raise Exception(f"SurrealDB error: {error_msg}")
            if "result" in result:
                res = result["result"]
                if isinstance(res, list):
                    return res
                elif res is not None:
                    return [res]
            return [result]
        return []

    async def create(self, table: str, data: Dict[str, Any], record_id: Optional[str] = None) -> Dict[str, Any]:
        if record_id:
            query = f"CREATE {table}:{record_id} SET {self._dict_to_set(data)};"
        else:
            query = f"CREATE {table} SET {self._dict_to_set(data)};"
        result = await self.query(query)
        if result:
            return result[0]
        return {}

    async def select(self, table: str, record_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if record_id:
            query = f"SELECT * FROM {table}:{record_id};"
        else:
            query = f"SELECT * FROM {table};"
        return await self.query(query)

    async def relate(self, from_table: str, from_id: str, relation: str, to_table: str, to_id: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if data:
            set_clause = f" SET {self._dict_to_set(data)}"
        else:
            set_clause = ""
        query = f"RELATE {from_table}:{from_id}->{relation}->{to_table}:{to_id}{set_clause};"
        result = await self.query(query)
        if result:
            return result[0]
        return {}

    def _dict_to_set(self, data: Dict[str, Any]) -> str:
        parts = []
        for key, value in data.items():
            if isinstance(value, str):
                parts.append(f"{key} = '{value}'")
            elif isinstance(value, (int, float, bool)):
                parts.append(f"{key} = {value}")
            else:
                parts.append(f"{key} = {value}")
        return ", ".join(parts)

    async def close(self) -> None:
        await self.client.aclose()

