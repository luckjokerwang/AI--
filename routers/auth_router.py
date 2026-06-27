from fastapi import APIRouter, Query, Depends
from pydantic import EmailStr
from typing import Annotated
from dependencies import get_mail, get_session
from fastapi_mail import FastMail, MessageSchema, MessageType
from models import AsyncSession
from respository.user_repo import EmailCodeRepository
from schemas import ResponseOut
import string
import random

router = APIRouter(prefix="/auth", tags=["user"])


@router.get("/code", response_model=ResponseOut)
async def get_mail_code(
    email: Annotated[EmailStr, Query(...)],
    mail: FastMail = Depends(get_mail),
    session: AsyncSession = Depends(get_session),
):
    # 生成验证码
    source = string.digits * 4
    code = "".join(random.choices(source, k=4))
    # 创建消息对象
    message = MessageSchema(
        subject="AI取名验证码",
        recipients=[email],
        body=f"您的验证码是：{code}，请在10分钟内完成验证。",
        subtype=MessageType.plain,
    )
    await mail.send_message(message)
    # 将验证码存入数据库
    return ResponseOut()
