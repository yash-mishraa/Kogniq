import re

with open('apps/web/src/components/documents/DocumentSurface.tsx', 'r') as f:
    content = f.read()

content = content.replace(
    '''className="flex w-full h-full transition-all duration-500 ease-[cubic-bezier(0.16,1,0.3,1)] flex-col max-w-5xl mx-auto"''',
    '''className="flex w-full h-full transition-all duration-500 ease-[cubic-bezier(0.16,1,0.3,1)] flex-col"'''
)

with open('apps/web/src/components/documents/DocumentSurface.tsx', 'w') as f:
    f.write(content)
