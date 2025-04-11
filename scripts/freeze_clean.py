import subprocess

output = subprocess.check_output(['pip', 'freeze']).decode()

lines = output.splitlines()
new_lines = []

for line in lines:
    if line.startswith('-e git+') and 'egg=mincal' in line:
        new_lines.append('-e .')
    else:
        new_lines.append(line)

with open('requirements.txt', 'w') as f:
    f.write('\n'.join(new_lines) + '\n')

print("✅ requirements.txt updated with -e . instead of -e git+...")