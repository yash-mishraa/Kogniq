import re

with open('apps/web/src/components/knowledge/KnowledgeEmptyState.tsx', 'r') as f:
    content = f.read()

content = content.replace(
    'Concepts and relationships will emerge here after knowledge extraction.',
    'Select a document from the Documents workspace to explore its knowledge graph.'
)

with open('apps/web/src/components/knowledge/KnowledgeEmptyState.tsx', 'w') as f:
    f.write(content)
