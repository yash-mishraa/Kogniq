import re

with open('apps/api/src/apps/api/app/routers/student.py', 'r') as f:
    content = f.read()

content = content.replace(
    'from fastapi import APIRouter, Depends, Header',
    'from fastapi import APIRouter, Depends, Header, Request'
)

content = content.replace(
    'authorization: str = Header(..., description="Bearer token")',
    'request_obj: Request, authorization: str | None = Header(None, description="Bearer token")'
)

content = content.replace(
    '''token = (
        authorization.replace("Bearer ", "")
        if authorization.startswith("Bearer ")
        else authorization
    )''',
    '''token = request_obj.cookies.get("kogniq_session", "") or (authorization.replace("Bearer ", "") if authorization and authorization.startswith("Bearer ") else (authorization or ""))'''
)

with open('apps/api/src/apps/api/app/routers/student.py', 'w') as f:
    f.write(content)
