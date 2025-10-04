"""Script to create initial superuser."""

import asyncio
from config.database import AsyncSessionLocal
from driven.db.users.adapter import UsersDBRepositoryAdapter
from application.services.users_service import UsersService


async def create_initial_superuser():
    """Create the initial superuser if it doesn't exist."""
    print("=" * 80)
    print("CREATE INITIAL SUPERUSER")
    print("=" * 80)

    async with AsyncSessionLocal() as session:
        users_repo = UsersDBRepositoryAdapter(session)
        users_service = UsersService(users_repo)

        # Default superuser credentials
        email = "admin@example.com"
        password = "admin123"  # Change this in production!
        full_name = "System Administrator"

        print(f"\nAttempting to create superuser: {email}")

        try:
            user = await users_service.create_superuser_if_not_exists(
                email=email,
                password=password,
                full_name=full_name
            )

            if user:
                await session.commit()
                print(f"✅ Superuser created successfully!")
                print(f"   Email: {email}")
                print(f"   Password: {password}")
                print(f"\n⚠️  IMPORTANT: Change the password after first login!")
            else:
                print(f"ℹ️  Superuser with email {email} already exists.")

        except Exception as e:
            await session.rollback()
            print(f"❌ Error creating superuser: {e}")
            raise

    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(create_initial_superuser())
