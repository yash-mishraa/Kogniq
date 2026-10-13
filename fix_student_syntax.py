import re

with open('apps/api/src/apps/api/app/routers/student.py', 'r') as f:
    content = f.read()

content = content.replace(
    'limit: int = Query(5, ge=1, le=100, description="Max recommendations to return"),\n    request_obj: Request,',
    'request_obj: Request,\n    limit: int = Query(5, ge=1, le=100, description="Max recommendations to return"),'
)

with open('apps/api/src/apps/api/app/routers/student.py', 'w') as f:
    f.write(content)
