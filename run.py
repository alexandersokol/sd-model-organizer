import os


def get_files(path):
    files = []
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        if os.path.isdir(file_path):
            files.extend(get_files(file_path))
        else:
            files.append(file_path)
    return files

def get_files_2(rootdir):
    extensions = ('.bin', '.ckpt', '.safetensors')
    result = []
    for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            ext = os.path.splitext(file)[-1].lower()
            if ext in extensions:
                filepath = os.path.join(subdir, file)
                result.append(filepath)
    return result

path = '/Users/alexander/Projects/Python/mo_files/models/Lora'
files = get_files_2(path)
for file in files:
    print(file.replace(path, ''))

print('Done. ')
