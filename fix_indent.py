import sys

with open('packages/application/src/application/agent/tutor_chat.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if line.startswith('        update_telemetry_context'):
        for j in range(i-1, i+6):
            if lines[j].startswith('        '):
                lines[j] = '    ' + lines[j]

with open('packages/application/src/application/agent/tutor_chat.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
