# DB Spyder - API Guide

## 🚀 Quick Start

### 1. Start the Server

```bash
source .venv/bin/activate
python run.py
```

Server will be available at `http://localhost:8000`

### 2. API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📡 API Endpoints

### Connections Management

#### List all connections
```bash
GET /api/v1/connections
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "My Database",
    "database_type": "postgresql",
    "host": "localhost",
    "port": 5432,
    "database": "mydb",
    "username": "user",
    "status": "active",
    "last_introspection": "2025-10-03T21:59:58.362331"
  }
]
```

#### Create connection
```bash
POST /api/v1/connections
Content-Type: application/json

{
  "name": "My PostgreSQL DB",
  "database_type": "postgresql",
  "host": "localhost",
  "port": 5432,
  "database": "mydb",
  "username": "postgres",
  "password": "secret",
  "db_schema": "public",
  "ssl_enabled": false
}
```

**Supported database types:**
- `postgresql`
- `mysql`
- `sqlite`

#### Get connection by ID
```bash
GET /api/v1/connections/{id}
```

#### Update connection
```bash
PUT /api/v1/connections/{id}
Content-Type: application/json

{
  "name": "Updated Name",
  "password": "new_password"
}
```

#### Delete connection
```bash
DELETE /api/v1/connections/{id}
```

#### Test connection
```bash
POST /api/v1/connections/test
Content-Type: application/json

{
  "name": "Test Connection",
  "database_type": "sqlite",
  "host": "localhost",
  "port": 0,
  "database": "test.db",
  "username": "",
  "password": "",
  "ssl_enabled": false
}
```

**Response:**
```json
{
  "success": true,
  "message": "Connection successful"
}
```

### Database Introspection

#### Introspect database
```bash
POST /api/v1/introspection
Content-Type: application/json

{
  "connection_id": 1
}
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully introspected database 'My Database'",
  "tables_count": 15,
  "relations_count": 23
}
```

#### Get discovered tables
```bash
GET /api/v1/introspection/connections/{connection_id}/tables
```

**Response:**
```json
[
  {
    "id": 1,
    "connection_id": 1,
    "table_name": "users",
    "schema_name": "public",
    "table_type": "TABLE",
    "row_count": null,
    "comment": null,
    "created_at": "2025-10-03T19:59:58.312280",
    "columns": [
      {
        "id": 1,
        "table_id": 1,
        "column_name": "id",
        "data_type": "INTEGER",
        "is_nullable": false,
        "is_primary_key": true,
        "is_foreign_key": false,
        "default_value": null,
        "max_length": null,
        "precision": null,
        "scale": null,
        "ordinal_position": 1
      }
    ]
  }
]
```

#### Get table by ID
```bash
GET /api/v1/introspection/tables/{table_id}
```

#### Get discovered relations
```bash
GET /api/v1/introspection/connections/{connection_id}/relations
```

**Response:**
```json
[
  {
    "id": 1,
    "from_table_id": 2,
    "to_table_id": 1,
    "from_column_id": 5,
    "to_column_id": 1,
    "relation_type": "many_to_one",
    "constraint_name": "fk_posts_user_id",
    "on_delete": "CASCADE",
    "on_update": "NO ACTION",
    "created_at": "2025-10-03T19:59:58.358826"
  }
]
```

#### Refresh metadata
```bash
POST /api/v1/introspection/connections/{connection_id}/refresh
```

#### Delete metadata
```bash
DELETE /api/v1/introspection/connections/{connection_id}/metadata
```

## 🧪 Testing with cURL

### Complete workflow example:

```bash
# 1. Create a connection
curl -X POST http://localhost:8000/api/v1/connections \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test SQLite",
    "database_type": "sqlite",
    "host": "localhost",
    "port": 0,
    "database": "test.db",
    "username": "",
    "password": "",
    "ssl_enabled": false
  }'

# Response: {"id": 1, ...}

# 2. Test the connection
curl -X POST http://localhost:8000/api/v1/connections/test \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test",
    "database_type": "sqlite",
    "host": "localhost",
    "port": 0,
    "database": "spyder_metadata.db",
    "username": "",
    "password": "",
    "ssl_enabled": false
  }'

# Response: {"success": true, "message": "Connection successful"}

# 3. Introspect the database
curl -X POST http://localhost:8000/api/v1/introspection \
  -H "Content-Type: application/json" \
  -d '{"connection_id": 1}'

# Response: {"success": true, "tables_count": 8, "relations_count": 8}

# 4. Get discovered tables
curl http://localhost:8000/api/v1/introspection/connections/1/tables | python -m json.tool

# 5. Get discovered relations
curl http://localhost:8000/api/v1/introspection/connections/1/relations | python -m json.tool
```

## 🐍 Testing with Python

Use the provided test script:

```bash
python test_api.py
```

Or with requests:

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Create connection
response = requests.post(f"{BASE_URL}/connections", json={
    "name": "My DB",
    "database_type": "sqlite",
    "host": "localhost",
    "port": 0,
    "database": "test.db",
    "username": "",
    "password": "",
    "ssl_enabled": False
})
connection = response.json()
print(f"Created connection: {connection['id']}")

# Introspect
response = requests.post(f"{BASE_URL}/introspection", json={
    "connection_id": connection['id']
})
result = response.json()
print(f"Found {result['tables_count']} tables")

# Get tables
response = requests.get(f"{BASE_URL}/introspection/connections/{connection['id']}/tables")
tables = response.json()
for table in tables:
    print(f"- {table['table_name']}: {len(table['columns'])} columns")
```

## 📊 Architecture

The API follows **Hexagonal Architecture**:

- **Domain**: Pure business entities (Connection, DiscoveredTable, etc.)
- **Application**: Services and ports (ConnectionsService, IntrospectionService)
- **Infrastructure**: Database inspectors (PostgreSQL, MySQL, SQLite)
- **Adapters**: 
  - Driven: Repository implementations
  - Driving: FastAPI routers

## 🔒 Security Notes

⚠️ **TODO**: Connection passwords are currently stored in plain text. Encryption should be implemented before production use.

## 📝 Error Handling

All endpoints return standard HTTP status codes:

- `200 OK` - Successful request
- `201 Created` - Resource created
- `204 No Content` - Successful deletion
- `400 Bad Request` - Invalid input
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error
- `503 Service Unavailable` - Database connection failed

Error response format:
```json
{
  "detail": "Error message here"
}
```
