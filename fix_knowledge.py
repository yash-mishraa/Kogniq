import re

with open('apps/api/src/apps/api/app/routers/knowledge.py', 'r') as f:
    content = f.read()

content = re.sub(
    r'token = \(\s*authorization\.replace\("Bearer ", ""\)\s*if authorization\.startswith\("Bearer "\)\s*else authorization\s*\)',
    'token = request_obj.cookies.get("kogniq_session", "") or (authorization.replace("Bearer ", "") if authorization and authorization.startswith("Bearer ") else (authorization or ""))',
    content,
    flags=re.MULTILINE
)

with open('apps/api/src/apps/api/app/routers/knowledge.py', 'w') as f:
    f.write(content)
