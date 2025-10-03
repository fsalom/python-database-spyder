"""Test script for database inspectors."""

import asyncio
from domain.entities.connection import Connection, DatabaseType
from infrastructure.inspectors.inspector_factory import InspectorFactory


async def test_sqlite_inspector():
    """Test SQLite inspector with the metadata database."""

    # Create connection to our SQLite metadata database
    connection = Connection(
        name="Spyder Metadata DB",
        database_type=DatabaseType.SQLITE,
        host="localhost",  # Not used for SQLite
        port=0,  # Not used for SQLite
        database="spyder_metadata.db",  # Our existing DB
        username="",  # Not used for SQLite
        password="",  # Not used for SQLite
    )

    # Create inspector
    inspector = InspectorFactory.create_inspector(connection)

    print("=" * 70)
    print("Testing SQLite Inspector")
    print("=" * 70)

    # Test connection
    print("\n1. Testing connection...")
    is_connected = await inspector.test_connection(connection)
    print(f"   Connection successful: {is_connected}")

    if not is_connected:
        print("   ❌ Could not connect to database")
        return

    # Inspect tables
    print("\n2. Inspecting tables...")
    tables = await inspector.inspect_tables(connection)
    print(f"   Found {len(tables)} tables:")

    for table in tables:
        print(f"\n   📊 Table: {table.table_name}")
        print(f"      Schema: {table.schema_name}")
        print(f"      Columns: {len(table.columns)}")

        for col in table.columns:
            pk_marker = " 🔑" if col.is_primary_key else ""
            fk_marker = " 🔗" if col.is_foreign_key else ""
            nullable = "NULL" if col.is_nullable else "NOT NULL"
            print(f"         - {col.column_name}: {col.data_type} {nullable}{pk_marker}{fk_marker}")

    # Inspect relations
    print("\n3. Inspecting relations...")
    relations = await inspector.inspect_relations(connection)
    print(f"   Found {len(relations)} foreign key relationships:")

    for rel in relations:
        print(f"      {rel.from_table_name}.{rel.from_column_name} → {rel.to_table_name}.{rel.to_column_name}")
        print(f"         ON DELETE: {rel.on_delete}, ON UPDATE: {rel.on_update}")

    print("\n" + "=" * 70)
    print("✅ Inspector test completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_sqlite_inspector())
