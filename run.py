with open('settings.txt') as f:
    lines = f.readlines()

my_dict = {}
for line in lines:
    key, value = line.strip().split(': ')
    my_dict[key] = value

print('hello')
print(my_dict)