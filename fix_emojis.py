with open('apps/web/src/app/workspace/environments/study/TutorChatPanel.tsx', 'r', encoding='utf-8') as f:
    text = f.read()
text = text.replace('o', '✨')
text = text.replace('o"', '✅')
text = text.replace('Y"?', '🔧')
with open('apps/web/src/app/workspace/environments/study/TutorChatPanel.tsx', 'w', encoding='utf-8') as f:
    f.write(text)
