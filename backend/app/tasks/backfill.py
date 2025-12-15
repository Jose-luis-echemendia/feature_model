import asyncio
from sqlalchemy import select, update, func
from app.models import User
from app.api.deps import AsyncSessionLocal


BATCH = 1000


async def migrate_phone_to_phone_number(batch_size: int = BATCH):
    async with AsyncSessionLocal() as session:
        while True:
            q = select(User.id, User.phone).where(User.phone_number == None).limit(batch_size)
            res = await session.execute(q)
            rows = res.all()
            if not rows:
                break


            ids = [r.id for r in rows]


            stmt = (
            update(User)
            .where(User.id.in_(ids))
            .values(phone_number=func.coalesce(User.phone, ''))
            )
            await session.execute(stmt)
            await session.commit()
            await asyncio.sleep(0.1)


if __name__ == '__main__':
    asyncio.run(migrate_phone_to_phone_number())