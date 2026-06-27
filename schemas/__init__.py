from pydantic import BaseModel,Field
from typing import Annotated,Literal

class ResponseOut(BaseModel):
    # 用于前端用户,只要返回结果
    result:Annotated[Literal["success","failsure"],Field( "success",description="请求的结果")]