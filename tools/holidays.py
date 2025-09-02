names = (
    'Январь', 'Февраль', 'Март',
    'Апрель', 'Май', 'Июнь',
    'Июль', 'Август', 'Сентябрь',
    'Октябрь', 'Ноябрь', 'Декабрь'
)


def parse(year: int):
    import datetime
    import requests
    from bs4 import BeautifulSoup
    from lxml import etree

    webpage = requests.get(f'https://online.zakon.kz/accountant/Calendars/Holidays/{year}', verify=False)
    soup = BeautifulSoup(webpage.content, "html.parser")
    dom = etree.HTML(str(soup))
    months = dom.xpath('//div[@class="month-col--calendar"]')

    data = dict()
    total_count = 0
    for month in months:
        month_name = month.xpath('.//h6')[0].text
        holidays = month.xpath(
            './/div[not(contains(@class, "prev-month")) and contains(@class, "calendar-day") '
            'and contains(@class, "holiday")]/span'
        )
        idx = names.index(month_name) + 1
        data[idx] = [int(r.text.strip()) for r in holidays]
        total_count += len(data[idx])

    web_holidays_count = int(dom.xpath('//div[contains(text(), "выходных дней")]/h2')[0].text)
    web_superholidays_count = int(dom.xpath('//div[contains(text(), "праздничных дней")]/h2')[0].text)
    if total_count != web_holidays_count + web_superholidays_count:
        raise Exception('Количество с портала не соответствует выгруженному количеству')

    result = list()
    for month in data:
        for day in data[month]:
            result.append(datetime.date(year, month, day))
    return result


if __name__ == '__main__':
    list(print(r) for r in parse(2023))
