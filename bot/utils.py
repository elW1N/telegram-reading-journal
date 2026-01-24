def pluralize_books(n):
    '''Склонение слова'''
    if 11 <= n % 100 <= 19:
        return "книг"
    elif n % 10 == 1:
        return "книга"
    elif 2 <= n % 10 <= 4:
        return "книги"
    else:
        return "книг"
