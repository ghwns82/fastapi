# 표준 라이브러리
import logging
from datetime import datetime
import time
from starlette.middleware.base import BaseHTTPMiddleware

# 서버
from fastapi import FastAPI, Request

#프로젝트 내부
from service import service_router
from attendance import attendance_router

app = FastAPI(
    title="Face-Rec Service",
    version="1.0.0",
)

@app.get('/')
async def welcome() -> dict:
    return {"message": "Hello World"}


app.include_router(router=service_router)
app.include_router(router=attendance_router)

class MyMiddleware(BaseHTTPMiddleware):

    # dispatch라는 함수에 실행을 원하는 로직을 적어야 함
    async def dispatch(self, request: Request, call_next):
        # 요청이 들어오기 전: 시작 시간 기록
        start_time = time.time()
        
        # call_next를 호출하면 실제 API 함수를 실행
        response = await call_next(request)
        
        # API 함수 호출이 종료되고 이후의 로직이 실행
        process_time = time.time() - start_time
        print(f"{datetime.now():%Y-%m-%d %H:%M:%S} Completed in {process_time:.2f} seconds")
        response.headers["X-Process-Time"] = f"{process_time:.2f}"
        return response
app.add_middleware(MyMiddleware)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port = 8080)