import re

with open('apps/web/src/components/documents/DocumentCollection.tsx', 'r') as f:
    content = f.read()

content = content.replace(
    '''className="flex flex-col flex-shrink-0 overflow-y-auto transition-all duration-500 w-full pt-12 px-6 lg:px-12 bg-transparent"''',
    '''className="flex flex-col flex-shrink-0 overflow-y-auto transition-all duration-500 w-full max-w-5xl mx-auto pt-12 px-6 lg:px-12 bg-transparent"'''
)

with open('apps/web/src/components/documents/DocumentCollection.tsx', 'w') as f:
    f.write(content)
