import sys
content = open('apps/web/src/app/workspace/environments/study/TutorChatPanel.tsx', 'r', encoding='utf-8').read()
content = content.replace('PoST', 'POST').replace('JSoN', 'JSON').replace('o\"', '✓').replace('-', '✖').replace('Y\"?', '⚙️')
open('apps/web/src/app/workspace/environments/study/TutorChatPanel.tsx', 'w', encoding='utf-8').write(content)
