import re

for filepath in ['apps/web/src/components/notebook/NotebookEmptyState.tsx', 'apps/web/src/components/study/StudyEmptyState.tsx']:
    with open(filepath, 'r') as f:
        content = f.read()

    content = content.replace(
        'const suggestions = [];',
        'const suggestions: { label: string; detail: string }[] = [];'
    )

    with open(filepath, 'w') as f:
        f.write(content)
