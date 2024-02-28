import datetime
import os
import random
import socket
import time
from contextlib import suppress

from math import ceil
from time import sleep
import pandas as pd
import pyautogui as pag

from tools.tg import tg_send
from tools.web import Web

import concurrent.futures


ip_address = socket.gethostbyname(socket.gethostname())


def human_imitation():
    positions = [[1137, 636], [1108, 656], [1101, 662], [1077, 674], [1013, 689], [900, 695], [798, 666], [771, 589], [801, 534], [882, 568], [1138, 705], [1229, 733], [1325, 742], [1485, 740], [1613, 647], [1456, 456], [1284, 505], [951, 666], [574, 749], [458, 718], [398, 572], [611, 424], [780, 493], [961, 685], [1169, 756], [1386, 769], [1521, 751], [1608, 676], [1478, 540], [1112, 504], [981, 663], [639, 859], [333, 677]]

    for i in positions:
        # x = -1000
        # y = -1000
        #
        # x_ = x if x > 250 else 250
        # y_ = y if y > 250 else 250

        pag.moveTo(i[0] + random.randint(-65, 65), i[1] + random.randint(-65, 65))


groups_list = []


def get_all_subcategories():

    global groups_list

    web = Web()

    web.run()

    main_url = 'https://kaspi.kz/shop/c/computers/?c='

    web.get(main_url)

    web.execute_script_click_xpath_selector("//a[contains(text(), 'Алматы')]")

    web.get(main_url)

    sleep(random.uniform(4.7, 5.4))

    subcategories_ = web.find_elements('//li[@class="tree__item  _expandable"]')

    subcategories_list = []

    for ind in range(1, len(subcategories_) + 1):

        subcategories_list.append(web.find_element(f'(//li[@class="tree__item  _expandable"]/span[1])[1]').get_attr('text'))
        web.execute_script_click_xpath_selector(f'(//li[@class="tree__item  _expandable"])[1]')
        # web.execute_script_click_xpath_selector(subcategory__)
        # web.find_element(subcategory__).click()

    groups = web.find_elements('//li[@class="tree__item "]/span[contains(@class, "tree__link") and not(contains(@class, "expanded"))]')

    for group_ in groups:
        groups_list.append(group_.get_attr('text'))

    web.quit()

    return [subcategories_list, groups_list]


def performer(web, main_url, task_id):

    print('\n=======================================================================================')

    web.get(main_url)

    sleep(random.uniform(2.7, 4.4))

    df = pd.DataFrame(columns=['title', 'link', 'subcategory', 'item_code', 'rassrochka', 'reviews_count', 'rating', 'avg_rating_last_month', 'reviews_last_month', 'sellers_info'])
    # subcategory.click()

    name = groups_list[0]
    groups_list.remove(name)
    print(len(groups_list))

    web.execute_script_click_xpath_selector(f'//span[contains(text(), "{name}")]')

    web.wait_element('//*[@id="scroll-to"]/div[4]/div[1]/div[1]/div[2]/div[1]/a')

    sleep(3)

    total_reviews_of_cat = int(web.find_element(f'//span[contains(text(), "{name}")]/../span[2]').get_attr('text').replace('(', '').replace(')', ''))
    print('TOTAL REVIEWS:', total_reviews_of_cat)

    with open(f'txts\\{task_id}.txt', 'a') as f:
        f.write(f"\n{datetime.datetime.now()} | Task {task_id} is running. Current word: {name}\n")

    subcategory_name = name

    print(subcategory_name)
    print('--------------------------')
    tg_send(f'Начали подкатегорию: {subcategory_name}\nМашина: {ip_address}\nПоток: {task_id}', bot_token=bot_token, chat_id=chat_id)

    saving_path = f'working_path\\{name}'

    os.makedirs(saving_path, exist_ok=True, mode=True)

    all_items = []
    c = 0

    # if total_reviews_of_cat > 1010:
        #
        # web.execute_script_click_xpath_selector("//div[@class='rating _small _2']")
        # web.wait_element('//*[@id="scroll-to"]/div[4]/div[1]/div[1]/div[2]/div[1]/a', timeout=10)
    web.execute_script_click_xpath_selector("//li[contains(@class, 'select__list-item') and text()='Высокий рейтинг']")

    sleep(2)

    if web.wait_element('//*[@id="scroll-to"]/div[4]/div[1]/div[1]/div[2]/div[1]/a'):

        while True:

            items = web.find_elements('//*[@id="scroll-to"]/div[4]/div[1]//div[2]/div[1]/a', timeout=60)

            for item in items:

                for tries in range(5):
                    try:
                        title = item.get_attr('text')
                        link = item.get_attr('href')
                        # print(datetime.datetime.now(), '|', title, link)

                        dick = dict()

                        try:
                            reviews_count = int(item.find_element('/../following-sibling::div/a', timeout=1).get_attr('text').split()[0][1:])
                            rating = int(item.find_element('/..//following-sibling::div[@class="item-card__rating"]/span').get_attr('class').split()[-1].replace('_', '')) / 2.0
                        except:
                            reviews_count = 0
                            rating = 0
                        # print(datetime.datetime.now(), '|', reviews_count, rating)

                        dick.update({'title': title, 'link': link, 'reviews_count': reviews_count, 'rating': rating})

                        all_items.append(dick.copy())

                        break

                    except:
                        sleep(3)
                        web.driver.refresh()
                        sleep(5)

            # reviews = web.find_elements('//*[@id="scroll-to"]/div[4]/div[1]//div[2]/div[2]/a')  # Need to find text

            class_ = 'disabled'

            web.scroll_to_bottom()

            if web.wait_element("//li[contains(text(), 'Следующ')]", timeout=.1): # Если продавцов меньше 6, то не будет следующей страницы
                class_ = web.find_element("//li[contains(text(), 'Следующ')]", timeout=.1).get_attr('class')

            if 'disabled' in class_:
                break
            c += 4
            print(datetime.datetime.now(), '|', 'Clicking on the next page of the subcategory')
            web.execute_script_click_xpath_selector("//li[contains(text(), 'Следующ')]")
            sleep(random.uniform(2.5, 4))
            print('--------------------------------------------------------')

    # ? ----- Iterate each item -----
    print('TOTAL FOUND ITEMS:', len(all_items))
    tg_send(f'Всего товаров: {len(all_items)}', bot_token=bot_token, chat_id=chat_id)
    all_items_executed_time = time.time()

    for ind_, item in enumerate(all_items):

        for tries in range(5):
            try:
                print(datetime.datetime.now(), '|', item)

                web.get(item['link'])

                item_code = web.find_element('//*[@id="ItemView"]/div[2]/div/div[2]/div/div[1]/div[1]').get_attr('text')

                print(datetime.datetime.now(), '|', item_code)

                item_code = int(item_code.replace('Код товара: ', ''))

                all_sellers_off_cur_item = []

                if ind_ % 6 == 0 and ind_ != 0:
                    human_imitation()

                while True:

                    single_seller = dict()

                    sellers_on_page = web.find_elements('//*[@id="offers"]/div/div/div[1]/table/tbody/tr', timeout=30)

                    for sellers_count in range(1, len(sellers_on_page) + 1):

                        seller, seller_rating, seller_reviews, seller_price, seller_delivery = 'Нет продавца', 0, 0, -1, ''

                        if web.wait_element(f'//*[@id="offers"]/div/div/div[1]/table/tbody/tr[{sellers_count}]/td[1]/a', timeout=.3):
                            seller = web.find_element(f'//*[@id="offers"]/div/div/div[1]/table/tbody/tr[{sellers_count}]/td[1]/a').get_attr('text')
                        if web.wait_element(f'//*[@id="offers"]/div/div/div[1]/table/tbody/tr[{sellers_count}]/td[1]/div/div', timeout=.1):
                            seller_rating = web.find_element(f'//*[@id="offers"]/div/div/div[1]/table/tbody/tr[{sellers_count}]/td[1]/div/div').get_attr('class').split()[-1].replace('_', '')
                        if web.wait_element(f'//*[@id="offers"]/div/div/div[1]/table/tbody/tr[{sellers_count}]/td[1]/div/a', timeout=.1):
                            seller_reviews = int((web.find_element(f'//*[@id="offers"]/div/div/div[1]/table/tbody/tr[{sellers_count}]/td[1]/div/a').get_attr('text')).split()[0][1:])
                        if web.wait_element(f'//*[@id="offers"]/div/div/div[1]/table/tbody/tr[{sellers_count}]/td[4]/div', timeout=.1):
                            seller_price = web.find_element(f'//*[@id="offers"]/div/div/div[1]/table/tbody/tr[{sellers_count}]/td[4]/div').get_attr('text').replace('₸', '').replace(' ', '')
                        if web.wait_element(f'//*[@id="offers"]/div/div/div[1]/table/tbody/tr[{sellers_count}]/td[3]/div//span', timeout=.1):
                            seller_delivery = web.find_elements(f'//*[@id="offers"]/div/div/div[1]/table/tbody/tr[{sellers_count}]/td[3]/div//span')

                        # print(datetime.datetime.now(), '|', seller)
                        #
                        # print(datetime.datetime.now(), '|', seller_rating)
                        #
                        # print(datetime.datetime.now(), '|', seller_reviews)
                        #
                        # print(datetime.datetime.now(), '|', seller_price)

                        # print('===')
                        seller_deliv, seller_pickup = '', ''
                        if seller_delivery != '':
                            for deliveries in seller_delivery:
                                if 'доставка' in deliveries.get_attr('text').lower():
                                    seller_deliv = deliveries.get_attr('text')
                                    # print(datetime.datetime.now(), '|', deliveries.get_attr('text'))
                                if 'самовывоз' in deliveries.get_attr('text').lower():
                                    seller_pickup = deliveries.get_attr('text')
                                    # print(datetime.datetime.now(), '|', deliveries.get_attr('text'))
                        # print('-------------------------------------')

                        single_seller.update({"продавец": f"{seller}", "рейтинг": float(seller_rating) / 2.0, "кол-во отзывов": seller_reviews, "цена продажи": int(seller_price), "доставка": f"{seller_deliv}", "самовывоз": f"{seller_pickup}"})

                        all_sellers_off_cur_item.append(single_seller.copy())

                        # ? ----- Next sellers page -----

                    class_ = 'disabled'

                    if web.wait_element("//li[contains(text(), 'Следующ')]", timeout=.1):  # Если продавцов меньше 6, то не будет следующей страницы
                        class_ = web.find_element("//li[contains(text(), 'Следующ')]", timeout=.05).get_attr('class')
                    if 'disabled' in class_:
                        break
                    print(datetime.datetime.now(), '|', 'Clicking on the next page')
                    web.execute_script_click_xpath_selector("//li[contains(text(), 'Следующ')]")

                # ? Имеется ли рассрочка

                # if web.wait_element('(//div[contains(text(), "В рассрочку")])[2]/following-sibling::div//span[1]', timeout=0):
                rassrochka = 0

                if web.wait_element('(//div[contains(text(), "В рассрочку")])[1]', timeout=.01):

                    rassrochka = (web.find_elements('(//div[contains(text(), "В рассрочку")])[2]/following-sibling::div//span')[-1]).get_attr('text')

                    rassrochka = int(rassrochka.split()[0])

                    print('RASSROCHKA:', rassrochka)

                # ? Собираем отзывы за последний месяц

                reviews_count_on_page = web.find_element("//li[contains(text(), 'Отзыв')]").get_attr('text')

                total_rating_last_month = 0
                total_feedbacks_last_month = 0

                if len(reviews_count_on_page) > 6:

                    web.execute_script_click_xpath_selector("//li[contains(text(), 'Отзыв')]")

                    if True:
                        web.execute_script_click_xpath_selector("//a[contains(text(), 'Новые')]")

                        if web.wait_element("//a[contains(text(), 'Показать ещё')]", timeout=.05):
                            for _ in range(4):

                                if web.wait_element("//a[contains(text(), 'Показать ещё')]", timeout=.001):
                                    print('Нажимаю на Показать ещё')
                                    web.execute_script_click_xpath_selector("//a[contains(text(), 'Показать ещё')]")

                                else:
                                    break

                        web.scroll_to_bottom()

                        if web.wait_element('//*[@id="reviews"]/div/div/div[2]/div[1]', timeout=10):

                            web.scroll_to_bottom()

                            feedbacks = web.find_elements('//*[@id="reviews"]/div/div/div[2]/div/header/div[1]')

                            for ind1, feedback in enumerate(feedbacks):

                                rating_ = int(feedback.get_attr('class').split()[-1].replace('_', '')) / 2.0
                                date_ = web.find_element(f"//*[@id='reviews']/div/div/div[2]/div[{ind1 + 1}]/header/div[1]/following-sibling::div[@class='reviews__date']").get_attr('text')
                                # date_ = feedbacks.find_element("")

                                day_ = int(date_.split('.')[0])
                                month_ = int(date_.split('.')[1])
                                year_ = int(date_.split('.')[2])

                                d = datetime.datetime(year_, month_, day_)

                                date_ = datetime.datetime.today()

                                if int((datetime.datetime.now() - d).days) <= 31:
                                    total_rating_last_month += rating_
                                    total_feedbacks_last_month += 1

                    # except Exception as error:
                    #     print(f'HUETA {error} | {task_id}, {ind_}, {name}')
                    #     sleep(1000)
                    #     raise Exception(f'HUETA {error} | {task_id}, {ind_}, {name}')

                if total_feedbacks_last_month > 0:
                    total_rating_last_month /= float(total_feedbacks_last_month * 1.0)

                df.loc[len(df)] = {'title': item['title'], 'link': item['link'], 'subcategory': subcategory_name, 'item_code': item_code, 'rassrochka': rassrochka,
                                   'reviews_count': item['reviews_count'], 'rating': item['rating'], 'avg_rating_last_month': total_rating_last_month,
                                   'reviews_last_month': total_feedbacks_last_month, 'sellers_info': all_sellers_off_cur_item}
                if len(df) % 5 == 0:
                    df_ = df.copy()
                    df_.columns = ['Название', 'Ссылка', 'Подкатегория', 'Код товара', 'Рассрочка, мес', 'Кол-во отзывов', 'Рейтинг', 'Средний рейтинг за посл. месяц', 'Кол-во отзывов за посл. месяц', 'Информация о продавцах']
                    df_.to_excel(os.path.join(saving_path, f"{datetime.datetime.now().strftime('%d_%m_%Y %H.%M.%S')}_{len(df)}.xlsx"), index=False)
                # web.page_back()
                sleep(random.uniform(2.7, 4.4))

                break

            except:
                sleep(random.uniform(5.7, 8.4))
                web.driver.refresh()
                sleep(random.uniform(5.8, 8.7))

    all_items_executed_time_end = time.time()
    print('\n=======================================================================================')

    tg_send(f'Закончили подкатегорию {subcategory_name}\nЗатраченное время: {all_items_executed_time_end - all_items_executed_time}с\nСреднее время на 1 товар: {ceil((all_items_executed_time_end - all_items_executed_time) / len(all_items))}с\nВсего товаров: {len(all_items)}\n\nМашина: {ip_address}\nПоток: {task_id}', bot_token=bot_token, chat_id=chat_id)
    df_ = df.copy()
    df_.columns = ['Название', 'Ссылка', 'Подкатегория', 'Код товара', 'Рассрочка, мес', 'Кол-во отзывов', 'Рейтинг', 'Средний рейтинг за посл. месяц', 'Кол-во отзывов за посл. месяц', 'Информация о продавцах']
    df_.to_excel(os.path.join(saving_path, f"{datetime.datetime.now().strftime('%d_%m_%Y %H.%M.%S')}_{len(df)}_{subcategory_name}.xlsx"), index=False)
    df_.to_excel(f"working_path\\{subcategory_name}.xlsx")

    print(f"{datetime.datetime.now()} | Task {task_id} finished. Current word: {name}")
    with open(f'txts\\{task_id}.txt', 'a') as f:
        f.write(f"{datetime.datetime.now()} | Task {task_id} finished. Current word: {name}\n")

    sleep(random.uniform(8.65, 12.67))

    web.get(main_url)

    return 0


def run_selenium(url, i):

    web_ = Web()

    web_.run()

    web_.driver.set_window_size(300, 700)

    web_.driver.set_window_position(500 * i, 30)

    web_.get(url)

    web_.execute_script_click_xpath_selector("//a[contains(text(), 'Алматы')]")

    web_.get(url)

    sleep(random.uniform(4.7, 5.4))

    return web_


if __name__ == '__main__':

    # a, b = get_all_subcategories()
    #
    # print(a)
    # print(len(a))
    #
    # print(b)
    # print(len(b))
    groups_list = ['Режущие плоттеры', 'Системы непрерывной подачи чернил', 'Блоки питания для стационарных телефонов', 'Аксессуары для стилусов', 'Сетевые карты', 'Серверы', 'Принтеры чеков и этикеток', 'Детекторы банкнот', 'IP-телефоны', 'Прочее программное обеспечение', '3D-принтеры', 'Емкости для отработанных чернил', 'Принтеры для печати пластиковых карт', 'Планшеты', 'Коммутаторы и маршрутизаторы', 'Серверные шкафы', 'Системные блоки', 'Счетчики банкнот', 'Аксессуары для сканеров штрих-кода', 'Спикерфоны', 'Сканеры', 'Фотополимерные смолы для 3D-печати', 'Автоподатчики для принтеров и МФУ', 'Стилусы', 'Усилители сотового сигнала', 'Трансиверы', 'Неттопы', 'Терминалы сбора данных', 'Аксессуары для торговых весов', 'Межсетевые шлюзы']


    bot_token = '************'
    chat_id = '***********'

    tg_send('Парсер запущен', bot_token=bot_token, chat_id=chat_id)

    main_url = 'https://kaspi.kz/shop/c/computers/?c='

    webs = []

    threads_num = 1

    for i in range(threads_num):

        webs.append(run_selenium(main_url, i))

    # subcategories = web.find_elements('//span[contains(@class, "tree__link")]')
    print(webs)

    tg_send(f'Всего категорий: {len(groups_list)}', bot_token=bot_token, chat_id=chat_id)

    # subcategories = web.find_elements('//span[contains(@class, "tree__link")]')
    #
    # subcategory = subcategories[counter]

    for ind in range(len(groups_list.copy())):

        performer(webs[0], main_url, 0)

    #
    # print('!!!NEW SUBCATEGORY!!!\n')
    # print(all_items)
    # tg_send(f'Закончили подкатегорию {subcategory_name}\nЗатраченное время: {all_items_executed_time_end - all_items_executed_time}с\nСреднее время на 1 товар: {ceil((all_items_executed_time_end - all_items_executed_time) / len(all_items))}с', bot_token=bot_token, chat_id=chat_id)
    # df_ = df.copy()
    # df_.columns = ['Название', 'Ссылка', 'Подкатегория', 'Код товара', 'Кол-во отзывов', 'Рейтинг', 'Средний рейтинг за посл. месяц', 'Кол-во отзывов за посл. месяц', 'Информация о продавцах']
    # df_.to_excel(f"working_path\\{subcategory_name}\\{datetime.datetime.now().strftime('%d_%m_%Y %H.%M.%S')}_{len(df)}_{subcategory_name}.xlsx")
    # df_.to_excel(f"working_path\\{subcategory_name}.xlsx")

    # web.get(main_url)

    for i in range(threads_num):
        webs[i].quit()

    # ? ----- end of iteration -----

    print('=======================================================================================')
    print('=======================================================================================')
    print('=======================================================================================')
    # df.to_excel(f"working_path\\{datetime.datetime.now().strftime('%d_%m_%Y %H.%M.%S')}_{len(df)}_MAIN.xlsx")

    # web.quit()

    # web.get(main_url)

    # sleep(24)
