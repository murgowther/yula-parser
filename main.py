from bs4 import BeautifulSoup
import requests
from selenium import webdriver
import time
import pandas
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
import openpyxl


def parser(url, data_list_count):
    #параметры запуска Selenium
    service = Service(executable_path='chromedriver.exe')
    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=Mozilla/5.0")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument('--log-level=3')
    options.add_argument("--headless")
    browser = webdriver.Chrome(service=service, options=options)
    try:
        browser.get(url)
        time.sleep(2)
        last_height = browser.execute_script("return document.body.scrollHeight")
        browser.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
        time.sleep(1)
        data_list_pages = []
        while True:
            data_list_pages.extend(get_content_page(browser.page_source))
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = browser.execute_script("return document.body.scrollHeight")
            if data_list_count == '':
                data_list_count = 1000
            if new_height == last_height:
                break
            last_height = new_height
            print(f'Собрано {len(data_list_pages)} лотов')
            if len(data_list_pages) >= int(data_list_count):
                break
        return data_list_pages
    except Exception as ex:
        print(f'Ошибка: {ex}')
        browser.close()
        browser.quit()
    browser.close()
    browser.quit()

def get_content_page(html):
    soup = BeautifulSoup(html, 'html.parser')
    blocks = soup.find_all('div', {"data-test-component": "ProductOrAdCard"})
    data_list = []
    for block in blocks:
        try:
            name = block.find('span', {'data-test-block': "ProductName"}).text
        except:
            name = 'Без названия'
        try:
            img_source = block.image.get('xlink:href')
            img_data = requests.get(img_source).content
            with open(f'img/{name}.jpg', 'wb') as handler:
                handler.write(img_data)
        except:
            img_source = 'Фото отсутствует'

        try:
            link = "https://youla.ru" + block.find('div').find('span').find('a').get('href')
        except:
            link = 'ссылка не найдена'
        if 'Без названия' in name:
            pass
        else:
            data_list.append({
                'name': name,
                'link': link,
                # 'img': img_source
            })

    return data_list

def save_exel(data):
    dataframe = pandas.DataFrame(data)
    writer = pandas.ExcelWriter(f'output.xlsx')
    dataframe.to_excel(writer, 'data_yula')
    writer._save()
    print(f'Завершено. Данные сохранены в файл "output.xlsx"')


if __name__ == "__main__":
    url = input('Введите ссылку:\n')
    data_list_count = input('Количество записей:\n')
    print('Сейчас сохранение фотографий происходит в папку img')
    print('Запуск парсера...')
    save_exel(parser(url, data_list_count))

