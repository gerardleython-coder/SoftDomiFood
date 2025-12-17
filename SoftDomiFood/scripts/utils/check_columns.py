import os, asyncio, asyncpg

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://softdomifood_user:softdomifood_pass@localhost:5432/softdomifood_db")

async def main():
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        cols = await conn.fetch("SELECT column_name FROM information_schema.columns WHERE table_name='orders' ORDER BY ordinal_position")
        print("columns:", [c['column_name'] for c in cols])
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
