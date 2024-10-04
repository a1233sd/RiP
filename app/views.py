from django.shortcuts import render

students = [
    {
        "id": 1,
        "name": "Хомякова Дарья Артёмовна",
        "course": 2,
        "group": "ИУ1-31Б",
        "number": "23У023",
        "image": "http://localhost:9000/images/1.png"
    },
    {
        "id": 2,
        "name": "Грибова Малика Максимовна",
        "course": 3,
        "group": "РК2-51Б",
        "number": "22Р034",
        "image": "http://localhost:9000/images/2.png"
    },
    {
        "id": 3,
        "name": "Любимов Матвей Степанович",
        "course": 1,
        "group": "Э6-11Б",
        "number": "24Э143",
        "image": "http://localhost:9000/images/3.png"
    },
    {
        "id": 4,
        "name": "Зубков Андрей Иванович",
        "course": 3,
        "group": "ИУ5Ц-71Б",
        "number": "21Ц010",
        "image": "http://localhost:9000/images/4.png"
    },
    {
        "id": 5,
        "name": "Никонов Михаил Леонидович",
        "course": 3,
        "group": "ЮР2-51Б",
        "number": "22Ю054",
        "image": "http://localhost:9000/images/5.png"
    },
    {
        "id": 6,
        "name": "Горбин Никита Петрович",
        "course": 4,
        "group": "СМ8-72Б",
        "number": "21С089",
        "image": "http://localhost:9000/images/6.png"
    }
]

draft_decree = {
    "id": 123,
    "status": "Черновик",
    "date_created": "12 сентября 2024г",
    "date": "3 октября 2024г",
    "students": [
        {
            "id": 1,
            "count": 2
        },
        {
            "id": 2,
            "count": 4
        },
        {
            "id": 3,
            "count": 5
        }
    ]
}


def getStudentById(student_id):
    for student in students:
        if student["id"] == student_id:
            return student


def getStudents():
    return students


def searchStudents(student_name):
    res = []

    for student in students:
        if student_name.lower() in student["name"].lower():
            res.append(student)

    return res


def getDraftDecree():
    return draft_decree


def getDecreeById(decree_id):
    return draft_decree


def index(request):
    student_name = request.GET.get("student_name", "")
    students = searchStudents(student_name) if student_name else getStudents()
    draft_decree = getDraftDecree()

    context = {
        "students": students,
        "student_name": student_name,
        "students_count": len(draft_decree["students"]),
        "draft_decree": draft_decree
    }

    return render(request, "students_page.html", context)


def student(request, student_id):
    context = {
        "id": student_id,
        "student": getStudentById(student_id),
    }

    return render(request, "student_page.html", context)


def decree(request, decree_id):
    decree = getDecreeById(decree_id)
    students = [
        {**getStudentById(student["id"]), "count": student["count"]}
        for student in decree["students"]
    ]

    context = {
        "decree": decree,
        "students": students
    }

    return render(request, "decree_page.html", context)
