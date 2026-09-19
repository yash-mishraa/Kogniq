import re

with open('apps/web/src/app/workspace/environments/learningHub/LearningHubEnvironment.tsx', encoding='utf-8') as f:
    code = f.read()

code = re.sub(r'style=\{\{ width: \$\((.*?)\)% \}\}', r'style={{ width: $(\1)% }}', code)

with open('apps/web/src/app/workspace/environments/learningHub/LearningHubEnvironment.tsx', 'w', encoding='utf-8') as f:
    f.write(code)
