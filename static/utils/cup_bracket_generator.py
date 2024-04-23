def generate_playoffs(num):
    classes_L = []
    classes_R = []
    current = num
    while current >= 2:
        classes_L.append({'class': ['L' + str(current), 'match']})
        classes_R.append({'class': ['R' + str(current), 'match']})
        current //= 2
    classes_L.append({'class': ['L' + str(num), 'match']})
    classes_R.append({'class': ['R' + str(num), 'match']})

    return {'left_playoffs': classes_L[::-1], 'right_playoffs': classes_R[::-1]}

for i in generate_playoffs(16)['left_playoffs']:
    print(i)