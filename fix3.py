
with open('apps/web/src/app/workspace/environments/learningHub/LearningHubEnvironment.tsx') as f:
    text = f.read()

text = text.replace('style={{ width: \% }}', 'style={{ width: \\%\ }}')

text = text.replace('style={{ width: \% }}', 'style={{ width: \\%\ }}')

with open('apps/web/src/app/workspace/environments/learningHub/LearningHubEnvironment.tsx', 'w') as out:
    out.write(text)

