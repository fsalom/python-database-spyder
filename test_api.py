"""Simple API test script to demonstrate DB Spyder functionality."""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"


def print_json(data):
    """Pretty print JSON data."""
    print(json.dumps(data, indent=2))


def test_api():
    """Test DB Spyder API endpoints."""
    print("=" * 80)
    print("DB SPYDER API TEST")
    print("=" * 80)

    # 1. Get all connections
    print("\n1️⃣  Getting all connections...")
    response = requests.get(f"{BASE_URL}/connections")
    connections = response.json()
    print(f"   Found {len(connections)} connection(s)")
    for conn in connections:
        print(f"   - {conn['name']} ({conn['database_type']})")

    if not connections:
        print("   No connections found. Please create one first.")
        return

    # Find SQLite connection
    sqlite_conn = next((c for c in connections if c['database_type'] == 'sqlite'), None)
    if not sqlite_conn:
        sqlite_conn = connections[0]

    connection_id = sqlite_conn['id']
    connection_name = sqlite_conn['name']

    # 2. Get specific connection
    print(f"\n2️⃣  Getting connection details (ID: {connection_id})...")
    response = requests.get(f"{BASE_URL}/connections/{connection_id}")
    connection = response.json()
    print(f"   Name: {connection['name']}")
    print(f"   Type: {connection['database_type']}")
    print(f"   Database: {connection['database']}")
    print(f"   Status: {connection['status']}")
    print(f"   Last introspection: {connection.get('last_introspection', 'Never')}")

    # 3. Introspect database
    print(f"\n3️⃣  Introspecting database '{connection_name}'...")
    response = requests.post(
        f"{BASE_URL}/introspection",
        json={"connection_id": connection_id}
    )
    result = response.json()
    print(f"   Success: {result['success']}")
    print(f"   Tables discovered: {result['tables_count']}")
    print(f"   Relations discovered: {result['relations_count']}")

    # 4. Get discovered tables
    print(f"\n4️⃣  Getting discovered tables...")
    response = requests.get(f"{BASE_URL}/introspection/connections/{connection_id}/tables")
    tables = response.json()
    print(f"   Found {len(tables)} table(s):")
    for table in tables[:5]:  # Show first 5
        print(f"   - {table['table_name']} ({len(table['columns'])} columns)")
    if len(tables) > 5:
        print(f"   ... and {len(tables) - 5} more")

    # 5. Get discovered relations
    print(f"\n5️⃣  Getting discovered relations...")
    response = requests.get(f"{BASE_URL}/introspection/connections/{connection_id}/relations")
    relations = response.json()
    print(f"   Found {len(relations)} relation(s)")

    # 6. Show detailed table info
    if tables:
        print(f"\n6️⃣  Detailed view of '{tables[0]['table_name']}' table...")
        table = tables[0]
        print(f"   Table: {table['table_name']}")
        print(f"   Schema: {table['schema_name']}")
        print(f"   Type: {table['table_type']}")
        print(f"   Columns ({len(table['columns'])}):")
        for col in table['columns'][:10]:  # Show first 10
            pk = " 🔑" if col['is_primary_key'] else ""
            fk = " 🔗" if col['is_foreign_key'] else ""
            nullable = "NULL" if col['is_nullable'] else "NOT NULL"
            print(f"      - {col['column_name']}: {col['data_type']} {nullable}{pk}{fk}")

    print("\n" + "=" * 80)
    print("✅ API TEST COMPLETED!")
    print("=" * 80)
    print(f"\n📚 API Documentation: http://localhost:8000/docs")
    print(f"🔍 OpenAPI Spec: http://localhost:8000/openapi.json")


if __name__ == "__main__":
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to API server.")
        print("   Make sure the server is running: python run.py")
    except Exception as e:
        print(f"❌ Error: {e}")
