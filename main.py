from fastapi import FastAPI,Depends
from fastapi_mail import FastMail,MessageSchema,MessageType
from dependencies import get_mail
# from aiosmtplib import SMTPConnectError
from routers.auth_router import router as auth_router

app = FastAPI()

app.include_router(auth_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/mail/test")
async def test_mail(email:str ,mail:FastMail=Depends(get_mail)):
    message = MessageSchema(
        subject="Hello from fastapi-mail",
        recipients=[email],
        subtype=MessageType.plain,
        body=f"Hello {email}, this is a test email from fastapi-mail"
    )
    try:
        await mail.send_message(message)
        return {"message": f"Email sent to {email} 成功"}
    except Exception as e:
        return {"message": f"Email sent to {email} 失败: {str(e)}"}
    