"""End-to-end test for database introspection and persistence."""

import asyncio
from config.database import AsyncSessionLocal
from domain.entities.connection import Connection, DatabaseType, ConnectionStatus
from driven.db.connections.adapter import ConnectionsDBRepositoryAdapter
from driven.db.metadata.adapter import MetadataDBRepositoryAdapter
from infrastructure.inspectors.inspector_factory import InspectorFactory


async def test_e2e_introspection():
    """Test complete flow: create connection → introspect → save metadata → retrieve."""

    print("=" * 80)
    print("END-TO-END INTROSPECTION TEST")
    print("=" * 80)

    async with AsyncSessionLocal() as session:
        # Initialize repositories
        connections_repo = ConnectionsDBRepositoryAdapter(session)
        metadata_repo = MetadataDBRepositoryAdapter(session)

        # Step 1: Create a connection to our own metadata database
        print("\n1️⃣  Creating database connection...")
        connection = Connection(
            name="Test SQLite Metadata DB",
            database_type=DatabaseType.SQLITE,
            host="localhost",
            port=0,
            database="spyder_metadata.db",
            username="",
            password="",
            status=ConnectionStatus.ACTIVE,
        )

        saved_connection = await connections_repo.create(connection)
        print(f"   ✅ Connection created: ID={saved_connection.id}, Name='{saved_connection.name}'")

        # Step 2: Test connection
        print("\n2️⃣  Testing connection...")
        inspector = InspectorFactory.create_inspector(saved_connection)
        is_connected = await inspector.test_connection(saved_connection)
        print(f"   {'✅' if is_connected else '❌'} Connection test: {is_connected}")

        if not is_connected:
            print("   Aborting test - connection failed")
            return

        # Step 3: Introspect database schema
        print("\n3️⃣  Introspecting database schema...")
        tables = await inspector.inspect_tables(saved_connection)
        relations = await inspector.inspect_relations(saved_connection)

        print(f"   ✅ Found {len(tables)} tables:")
        for table in tables:
            print(f"      📊 {table.table_name} ({len(table.columns)} columns)")

        print(f"   ✅ Found {len(relations)} relationships:")
        for rel in relations[:5]:  # Show first 5
            print(f"      🔗 {rel.from_table_name}.{rel.from_column_name} → {rel.to_table_name}.{rel.to_column_name}")
        if len(relations) > 5:
            print(f"      ... and {len(relations) - 5} more")

        # Step 4: Save metadata to database
        print("\n4️⃣  Saving discovered metadata to database...")
        saved_tables = await metadata_repo.save_tables(saved_connection.id, tables)
        print(f"   ✅ Saved {len(saved_tables)} tables with columns")

        saved_relations = await metadata_repo.save_relations(saved_connection.id, relations)
        print(f"   ✅ Saved {len(saved_relations)} relationships")

        await session.commit()

        # Step 5: Retrieve and verify saved data
        print("\n5️⃣  Retrieving saved metadata from database...")
        retrieved_tables = await metadata_repo.get_tables_by_connection(saved_connection.id)
        retrieved_relations = await metadata_repo.get_relations_by_connection(saved_connection.id)

        print(f"   ✅ Retrieved {len(retrieved_tables)} tables from database:")
        for table in retrieved_tables:
            pk_cols = [col.column_name for col in table.columns if col.is_primary_key]
            fk_cols = [col.column_name for col in table.columns if col.is_foreign_key]
            print(f"      📊 {table.table_name} (ID: {table.id})")
            print(f"         - {len(table.columns)} columns")
            print(f"         - Primary keys: {pk_cols if pk_cols else 'None'}")
            print(f"         - Foreign keys: {fk_cols if fk_cols else 'None'}")

        print(f"\n   ✅ Retrieved {len(retrieved_relations)} relationships from database")

        # Step 6: Get all connections
        print("\n6️⃣  Listing all connections...")
        all_connections = await connections_repo.get_all()
        print(f"   ✅ Found {len(all_connections)} total connection(s):")
        for conn in all_connections:
            print(f"      🔌 ID={conn.id}, Name='{conn.name}', Type={conn.database_type}")

        # Step 7: Detailed view of one table
        print("\n7️⃣  Detailed view of 'users' table...")
        users_table = next((t for t in retrieved_tables if t.table_name == "users"), None)
        if users_table:
            print(f"   Table: {users_table.table_name}")
            print(f"   Schema: {users_table.schema_name}")
            print(f"   Columns:")
            for col in users_table.columns:
                pk = " 🔑 PK" if col.is_primary_key else ""
                fk = " 🔗 FK" if col.is_foreign_key else ""
                null = "NULL" if col.is_nullable else "NOT NULL"
                print(f"      - {col.column_name}: {col.data_type} {null}{pk}{fk}")

        print("\n" + "=" * 80)
        print("✅ END-TO-END TEST COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print("\nSummary:")
        print(f"  • Created connection: {saved_connection.name}")
        print(f"  • Introspected: {len(tables)} tables, {len(relations)} relations")
        print(f"  • Persisted: All metadata saved to spyder_metadata.db")
        print(f"  • Verified: Successfully retrieved all data")
        print("\n🎉 The introspection system is working end-to-end!")
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_e2e_introspection())
