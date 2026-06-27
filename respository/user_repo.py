# from models import AsyncSession
# from models.user import User, EmailCode
# from sqlalchemy import select, update, delete, exists
# from datetime import datetime, timedelta

# class EmailCodeRepository:
#     def __init__(self, session: AsyncSession):
#         self.session = session

#     async def create(self, email: str, code: str) -> EmailCode:
#         async with self.session.begin():
#             email_code = EmailCode(email=email, code=code)
#             self.session.add(email_code)
#             return email_code

#     async def check_email_code(self, email: str, code: str) -> bool:
#         async with self.session.begin():
#             email_code: EmailCode|None = await self.session.scalar(select(EmailCode).filter(EmailCode.email==email, EmailCode.code==code))
#             if not email_code:
#                 return False
#             if (datetime.now() - email_code.create_time) > timedelta(minutes=10):
#                 return False
#             return True

from models import AsyncSession
from models.user import User, EmailCode
from sqlalchemy import select, update, delete, exists
from datetime import datetime, timedelta


class EmailCodeRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self,email:str,code:str) -> EmailCode:
        async with self.session.begin():
            email_code = EmailCode(email=email, code=code)
            self.session.add(email_code)
            return email_code

    async def check_email_code(self, email: str, code: str) -> bool:
        async with self.session.begin():
            email_code: EmailCode|None = await self.session.scalar(select(EmailCode).filter(EmailCode.email==email, EmailCode.code==code))
            if not email_code:
                return False
            if (datetime.now() - email_code.create_time) > timedelta(minutes=10):
                return False
            return True