import re

with open('apps/web/src/components/documents/DocumentCollection.tsx', 'r') as f:
    content = f.read()

content = content.replace(
    '''className="flex flex-col flex-1 h-full pt-16 px-6 lg:px-8 bg-[#fafafa]"''',
    '''className="flex flex-col flex-1 h-full pt-16 px-6 lg:px-8 bg-[#fafafa] max-w-5xl mx-auto w-full"'''
)

with open('apps/web/src/components/documents/DocumentCollection.tsx', 'w') as f:
    f.write(content)
