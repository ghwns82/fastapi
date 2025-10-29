# 표준 라이브러리
import asyncio
import io
import os

# 서버
from fastapi import FastAPI

#프로젝트 내부
from service import service_router

app = FastAPI(
    title="Face-Rec Service",
    version="1.0.0",
)

@app.get('/')
async def welcome() -> dict:
    return {"message": "Hello World"}


app.include_router(router=service_router)



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port = 8080)