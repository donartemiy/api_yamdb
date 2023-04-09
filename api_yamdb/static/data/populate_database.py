# Скрипт заполняет иаблицу sql lite из .csv файлов
import csv
import sqlite3


def sql_connection(name_db):
    """ Подключение к БД. """
    try:
        con = sqlite3.connect(name_db)
        print("SQLite. База данных подключена.")
        return con
    except sqlite3.Error as error:
        print('SQLite. Ошибка подключения к DB: ', error)


def sql_get_table_field(connect, name_table) -> list:
    """Возвращает список столбцов таблицы
    Output: ['id', 'name', 'description', 'year', 'category_id'] """
    try:
        cursor = connect.execute(f'select * from {name_table}')
        colomns = [description[0] for description in cursor.description]
        return colomns
    except sqlite3.Error as error:
        print('SQLite. Ошибка наполнения DB: ', error)


def sql_insert(connect, query, data):
    """ Записывает данные в таблицу БД. """
    try:
        cursor = connect.cursor()
        cursor.executemany(query, data)
        connect.commit()
        print("SQLite. Запись добавлена.")
        cursor.close()
    except sqlite3.Error as error:
        print('SQLite. Ошибка наполнения DB: ', error,
              '\nquery: ', query,
              '\ncur.fetchall(): ', cursor.fetchall(),
              '\ndata', data)


def csv_read(filename_csv) -> list:
    """ Читаем .csv и возвращаем данные в виде списка со словарями,
    где каждая строка это словарь, где key поле, а item значение. """
    data = []
    with open(filename_csv, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data.append(row)
    print('CSV. Файл прочитан')
    return data


def get_colomns(data) -> list:
    """ Из данных, полученных из .csv, получаем список полей. """
    colomns = []
    for col in data[0].keys():
        colomns.append(col)
    return colomns


def create_query(name_table, colomns) -> str:
    """ Формируем запрос в БД. """
    colomns = ', :'.join(colomns)
    colomns = ':' + colomns
    query = f"INSERT OR IGNORE INTO {name_table} VALUES({colomns})"
    return query


def add_empty_fields(diff_colomns, data):
    """ В даные, полученые из .csv, добавляем поля, которых не хватает. """
    for colomn in diff_colomns:
        for string in data:
            string[colomn] = ''
    return data


def main(filename_db, name_table, filename_csv):
    data = csv_read(filename_csv)
    colomns_csv = get_colomns(data)

    con = sql_connection(filename_db)
    colomns_table = sql_get_table_field(con, name_table)

    diff_colomns = list(set(colomns_table) - set(colomns_csv))
    data = add_empty_fields(diff_colomns, data)

    query = create_query(name_table, colomns_table)
    sql_insert(connect=con, query=query, data=tuple(data))


# Data
tables_and_csvs = (('reviews_category', 'category.csv'),
                   ('reviews_genre', 'genre.csv'),
                   ('reviews_title_genre', 'genre_title.csv'),
                   ('reviews_title', 'titles.csv'),
                   ('reviews_review', 'review.csv'),
                   ('reviews_comment', 'comments.csv'),
                   ('reviews_user', 'users.csv')
                   )

filename_csv = 'category.csv'

if __name__ == '__main__':
    for table in tables_and_csvs:
        main(filename_db='db8.sqlite3',
             name_table=table[0],
             filename_csv=table[1])
