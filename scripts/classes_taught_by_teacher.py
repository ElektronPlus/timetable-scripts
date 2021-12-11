import requests

json = requests.get('https://beta.elektronplus.pl/timetable').json()

teachers = json['legend']['nauczyciel']['options']

for teacher in teachers:
    teacher = {
        'id': 'n' + teacher['value'],
        'name': teacher['name'],
        'classes': set(),
    }

    teacher['lessons'] = json['plany'][teacher['id']]['tydzien']

    for day in teacher['lessons']:
        for lesson in day['lekcje']:
            class_name = lesson['data'][:3]

            if class_name != '':
                teacher['classes'].add(class_name)

    print(teacher['name'])
    print(sorted(teacher['classes']))
    print('-------')
