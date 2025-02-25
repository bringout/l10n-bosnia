from dbos import DBOSContextSetAuth
from fastapi.security import OAuth2PasswordBearer
from typing import Optional, Callable, Awaitable, List
from fastapi import Request, Response
import jwt
import datetime

# https://stackoverflow.com/questions/71525132/how-to-write-a-custom-fastapi-middleware-class

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class JwtMiddleware:

    async def __call__(
            self, 
            request: Request, 
            call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        print("jwtAuthMidlleware")
        user: Optional[str] = None
        roles: Optional[List[str]] = None
        try:
            #print("jwtAuthMidlleware-2")
            token = await oauth2_scheme(request)
            #print("jwtAuthMidlleware-3")
            if token is not None:
                #tdata = decode_jwt(token)
                print("token:", token)
                tdata = jwt.decode(token, options={"verify_signature": False})
                print(tdata)
                token_expires = datetime.datetime.fromtimestamp(tdata["exp"])
                token_released = datetime.datetime.fromtimestamp(tdata["iat"])
                print("token_released", token_released)
                print("token_expires", token_expires)

                user = tdata["email"]
                roles = tdata["realm_access"]["roles"]
                print("roles=", roles)
        except Exception as e:
            print("exception", e)
            pass

        with DBOSContextSetAuth(user, roles):
            print("user=", user, "call_next=", call_next)
            response = await call_next(request)
            return response