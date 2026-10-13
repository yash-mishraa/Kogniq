import re

with open('apps/web/src/components/notebook/NotebookEmptyState.tsx', 'r') as f:
    content = f.read()

content = content.replace(
    '''  const suggestions = [
    { label: "My Recent Notes", detail: "Updated today" },
    { label: "Archived Notes", detail: "Updated 1 week ago" },
  ];''',
    '''  const suggestions = [];'''
)

with open('apps/web/src/components/notebook/NotebookEmptyState.tsx', 'w') as f:
    f.write(content)
