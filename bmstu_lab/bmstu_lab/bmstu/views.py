from django.shortcuts import render
from datetime import date
from django.templatetags.static import static

def hello(request):
    return render(request, 'index.html', { 'data' : {
        'current_date': date.today(),
        'list': ['python', 'django', 'html']
    }})

def GetOrders(request):
    query = request.GET.get('q', '')
    students = [
        {
            'id': 1,
            'title': 'Хомякова Дарья Артёмовна',
            'photo_url': 'http://127.0.0.1:9002/image/1.jpg'
        },
        {
            'id': 2,
            'title': 'Грибова Малика Максимовна',
            'photo_url': 'http://127.0.0.1:9002/image/2.jpg'
        },
        {
            'id': 3,
            'title': 'Любимов Матвей Степанович',
            'photo_url': 'http://127.0.0.1:9002/image/3.jpg'
        },
        {
            'id': 4,
            'title': 'Зубков Андрей Иванович',
            'photo_url': 'http://127.0.0.1:9002/image/4.jpg'
        },
        {
            'id': 5,
            'title': 'Никонов Михаил Леонидович',
            'photo_url': 'http://127.0.0.1:9002/image/5.jpg'
        },
    ]
    
    # Если есть запрос на поиск, отфильтровываем студентов по ФИО
    if query:
        students = [student for student in students if query.lower() in student['title'].lower()]
    
    return render(request, 'orders.html', {'data': {
        'current_date': date.today(),
        'orders': students,
        'query': query
    }})

def GetOrder(request, id):
    students = {
        1: {
            'name': 'Хомякова Дарья Артёмовна',
            'group': 'ИУ1-31Б',
            'course': 2,
            'year': 2023,
            'student_id': '23У023',
            'photo_url': 'http://127.0.0.1:9002/image/1.jpg'  
        },
        2: {
            'name': 'Грибова Малика Максимовна',
            'group': 'РК2-51Б',
            'course': 3,
            'year': 2022,
            'student_id': '22Р034',
            'photo_url': 'http://127.0.0.1:9002/image/2.jpg'
        },
        3: {
            'name': 'Любимов Матвей Степанович',
            'group': 'Э6-11Б',
            'course': 1,
            'year': 2024,
            'student_id': '24Э143',
            'photo_url': 'http://127.0.0.1:9002/image/3.jpg'
        },
        4: {
            'name': 'Зубков Андрей Иванович',
            'group': 'ИУ5Ц-71Б',
            'course': 4,
            'year': 2021,
            'student_id': '21Ц010',
            'photo_url': 'http://127.0.0.1:9002/image/4.jpg'
        },
        5: {
            'name': 'Никонов Михаил Леонидович',
            'group': 'ЮР-51Б',
            'course': 3,
            'year': 2022,
            'student_id': '22Ю054',
            'photo_url': 'http://127.0.0.1:9002/image/5.jpg'
        },
    }
    student = students.get(id)
    
    if not student:
        # Обработка случая, когда студент с таким ID не найден
        return render(request, 'order.html', {'data': {
            'current_date': date.today(),
            'student': None,
            'error': 'Студент не найден.'
        }})
    
    return render(request, 'order.html', {'data': {
        'current_date': date.today(),
        'student': student
    }})

def sendText(request):
    input_text = request.POST['text']

def cart_view(request):
    return render(request, 'cart.html')

