from django.shortcuts import render, redirect, get_object_or_404
from .models import Students, Decree, DecreeStudents
from django.db import connection
from django.contrib import messages

def getStudentById(student_id):
    try:
        return Students.objects.get(id=student_id)
    except Students.DoesNotExist:
        return None

def getStudents():
    return Students.objects.all()

def searchStudents(student_name):
    return Students.objects.filter(name__icontains=student_name)

def index(request):
    student_name = request.GET.get("student_name", "")
    students = searchStudents(student_name) if student_name else getStudents()
    
    # Получаем текущую заявку из сессии или используем черновик
    decree_id = request.session.get('decree_id')
    if decree_id:
        try:
            draft_decree = Decree.objects.get(id=decree_id, status=1)
        except Decree.DoesNotExist:
            draft_decree = None
    else:
        draft_decree = None
    
    if not draft_decree:
        # Создаём новую заявку, если её нет
        draft_decree = Decree.objects.create(status=1)
        request.session['decree_id'] = draft_decree.id
    
    students_count = DecreeStudents.objects.filter(decree=draft_decree).count()
    
    context = {
        "students": students,
        "student_name": student_name,
        "students_count": students_count,
        "draft_decree": draft_decree
    }

    return render(request, "students_page.html", context)

def student(request, student_id):
    student_obj = getStudentById(student_id)
    if not student_obj:
        return redirect('index')  # Или отобразить страницу 404

    context = {
        "id": student_id,
        "student": student_obj,
    }

    return render(request, "student_page.html", context)

def view_decree(request, decree_id):
    decree = get_object_or_404(Decree, id=decree_id)
    students_in_decree = DecreeStudents.objects.filter(decree=decree)
    
    # Собираем подробную информацию о студентах
    students = [
        {
            "id": ds.student.id,
            "name": ds.student.name,
            "course": ds.student.course,
            "group": ds.student.group,
            "number": ds.student.number,
            "image": ds.student.image,
            "debt_count": ds.student.debt_count,
            "count": ds.count
        }
        for ds in students_in_decree
    ]
    
    context = {
        "decree": decree,
        "students": students
    }
    
    return render(request, 'decree_page.html', context)

def delete_decree(request, decree_id):
    # Получаем объект Decree по id
    decree = get_object_or_404(Decree, id=decree_id)
    
    # Удаляем всех студентов, связанных с этой заявкой
    DecreeStudents.objects.filter(decree=decree).delete()
    
    # Обновляем статус заявки на "Удалено"
    decree.status = 5
    decree.save()
    
    return redirect('index')


def add_to_decree(request, student_id):
    # Получаем текущую заявку из сессии
    decree_id = request.session.get('decree_id')
    
    if not decree_id:
        # Если нет, создаём новую заявку
        decree = Decree.objects.create(status=1)
        request.session['decree_id'] = decree.id
    else:
        decree = get_object_or_404(Decree, id=decree_id, status=1)
    
    student = get_object_or_404(Students, id=student_id)
    
    # Проверка, есть ли уже этот студент в заявке
    decree_student, created = DecreeStudents.objects.get_or_create(decree=decree, student=student)
    if not created:
        decree_student.count += 1
        decree_student.save()

    return redirect('index')

def remove_from_decree(request, decree_id, student_id):
    """
    Удаляет студента из заявки (корзины).
    """
    decree = get_object_or_404(Decree, id=decree_id)
    student = get_object_or_404(Students, id=student_id)
    
    # Пытаемся найти связующую запись DecreeStudents
    try:
        decree_student = DecreeStudents.objects.get(decree=decree, student=student)
        decree_student.delete()  # Удаляем запись
    except DecreeStudents.DoesNotExist:
        pass  # Можно добавить сообщение об ошибке, если необходимо
    
    return redirect('view_decree', decree_id=decree_id)

def view_deleted_decree(request, decree_id):
    decree = get_object_or_404(Decree, id=decree_id, status=5)
    students_in_decree = DecreeStudents.objects.filter(decree=decree)
    
    # Собираем подробную информацию о студентах
    students = [
        {
            "id": ds.student.id,
            "name": ds.student.name,
            "course": ds.student.course,
            "group": ds.student.group,
            "number": ds.student.number,
            "image": ds.student.image,
            "debt_count": ds.student.debt_count,
            "count": ds.count
        }
        for ds in students_in_decree
    ]
    
    context = {
        "decree": decree,
        "students": students
    }
    
    return render(request, 'deleted_decree.html', context)

def update_debt(request, decree_id, student_id):
    """
    Обновляет debt_count для конкретного студента.
    """
    decree = get_object_or_404(Decree, id=decree_id)
    student = get_object_or_404(Students, id=student_id)
    
    if request.method == 'POST':
        debt_count = request.POST.get('debt_count')
        if debt_count is not None:
            try:
                debt_count = int(debt_count)
                if debt_count < 0:
                    raise ValueError("Долги не могут быть отрицательными.")
                student.debt_count = debt_count
                student.save()
                messages.success(request, f'Долги студента {student.name} успешно обновлены.')
            except ValueError:
                messages.error(request, 'Некорректное значение долгов. Пожалуйста, введите неотрицательное число.')
        else:
            messages.error(request, 'Не указано значение долгов.')
    else:
        messages.error(request, 'Неверный метод запроса.')
    
    return redirect('view_decree', decree_id=decree_id)