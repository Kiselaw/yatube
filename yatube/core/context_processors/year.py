import datetime as dt


def year(request):
    """Добавляет переменную с текущим годом."""
    current_date = int(dt.datetime.now().year)
    return {
        'year': current_date
    }
