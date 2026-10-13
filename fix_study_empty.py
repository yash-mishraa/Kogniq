import re

with open('apps/web/src/components/study/StudyEmptyState.tsx', 'r') as f:
    content = f.read()

content = content.replace(
    '''  const suggestions = [
    { label: "Resume yesterday's study", detail: "Recent concepts" },
    { label: "Review your saved notes", detail: "Last studied yesterday" },
    { label: "Start a new session", detail: "Ready to study" },
  ];''',
    '''  const suggestions = [];'''
)

with open('apps/web/src/components/study/StudyEmptyState.tsx', 'w') as f:
    f.write(content)
