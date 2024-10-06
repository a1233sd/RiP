import psycopg2

# Подключение с использованием локального хоста (127.0.0.1)
conn = psycopg2.connect(dbname="postgres", host="127.0.0.1", user="postgres", password="1", port="5432")

cursor = conn.cursor()

# Пример запроса к базе данных
cursor.execute("INSERT INTO public.books (id, name, description) VALUES(1, 'Мастер и Маргарита', 'Крутая книга')")
cursor.execute("INSERT INTO public.books (id, name, description) VALUES(2, 'Война и мир', 'Эпическая история')")

conn.commit()  # Выполняем запрос

cursor.close()
conn.close()
