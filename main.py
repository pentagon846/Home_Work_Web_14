import dotenv
import uvicorn
from sqlalchemy.orm import Session
from sqlalchemy import text
from ipaddress import ip_address
from fastapi.responses import JSONResponse
from src.database.db import get_db
from src.routes import contacts, auth, users
from fastapi_limiter import FastAPILimiter
from src.conf.config import settings
import redis.asyncio as redis
from starlette.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, HTTPException, Request, status
from typing import Callable

app = FastAPI()


@app.on_event("startup")
async def startup():
    """
The startup function is called when the application starts up.
It's a good place to initialize things that are needed by your app,
such as connecting to databases or initializing caches.

:return: A list of coroutines to run
:doc-author: Trelent
"""
    r = await redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0)
    await FastAPILimiter.init(r)


app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://127.0.0.1:5500', 'http://localhost:5500'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ALLOWED_IPS = [ip_address('192.168.1.0'), ip_address('172.16.0.0'), ip_address("127.0.0.1")]


@app.middleware("http")
async def limit_access_by_ip(request: Request, call_next: Callable):
    """
The limit_access_by_ip function is a middleware function that limits access to the API by IP address.
It checks if the client's IP address is in ALLOWED_IPS, and if not, returns a 403 Forbidden response.

:param request: Request: Get the client's ip address
:param call_next: Callable: Pass the next function in the chain
:return: A jsonresponse object with a status code of 403 and a detail message
:doc-author: Trelent
"""
    ip = ip_address(request.client.host)
    if ip not in ALLOWED_IPS:
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": "Not allowed IP address"})
    response = await call_next(request)
    return response


@app.get("/")
async def root():
    """
The root function returns a JSON object with the message &quot;Hello World&quot;.

:return: A dictionary with a single key &quot;message&quot; and the value of that key is &quot;hello world&quot;
:doc-author: Trelent
"""
    return {"message": "Hello World"}


@app.get("/api/healthchecker")
def healthchecker(db: Session = Depends(get_db)):
    """
The healthchecker function is a simple function that checks the health of the database.
It does this by making a request to the database and checking if it returns any results.
If there are no results, then we know something is wrong with our connection.

:param db: Session: Get the database session
:return: A dictionary with a message
:doc-author: Trelent
"""
    try:
        # Make request
        result = db.execute(text("SELECT 1")).fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")


app.include_router(auth.router, prefix='/api')
app.include_router(users.router, prefix='/api')
app.include_router(contacts.router, prefix='/api')

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
