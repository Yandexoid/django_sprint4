import datetime as dt


def year(request):
    """Добавляет в контекст переменную с текущим годом."""
    return {
        'year': dt.datetime.now().year
    }
