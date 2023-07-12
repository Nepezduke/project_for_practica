"""
критерии оценки:
полное соответствие имени домена и названия организации: 10 из 10
найдено название организации, но оно не совпадает с название домена: 5 из 10
не найдено название организации или оно закрыто, но есть название домена: 2 из 10
не найдено название организации или оно закрыто и не найдено название домена: 0 из 10
"""

# Импорт необходимых модулей
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from urllib.parse import urlparse
import tldextract



#Запрашиваем URL-адрес у пользователя
input_url = input("Введите ссылку: ")

#Разбираем URL-адрес
parsed_url = urlparse(input_url)
domain_name = parsed_url.netloc

#Составляем новый URL-адрес для получения информации о домене
url = f"https://whois.ru/{domain_name}"

#Генерируем случайный user-agent
user_agent = UserAgent()

#Задаем заголовки для HTTP-запроса
headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'user-agent': user_agent.random
}



#Функция для поиска строки с информацией об организации
def find_org_string(area_string):
    lines = area_string.split("\n")
    for line in lines:
        if "org:" in line:
            return line.strip()
        if "person:" in line:
            return 'данные об организации закрыты!'
    return "данные об организации не найдены! "



# Функция для сравнения имени домена и названия организации
def compare_domain_and_organization(domain_name, org_info):

    # Извлекаем имя домена из доменного имени
    extracted = tldextract.extract(domain_name)
    domain = extracted.domain

    # Разделяем строку org_info по символу ':' и проверяем длину списка
    org_info_parts = org_info.lower().split(":")
    if len(org_info_parts) < 2:
        return " Данные об организации не найдены!  \nсоответсвие: 2 из 10"
    
    org_name = org_info_parts[1].strip().replace('"', "").replace("jsc ", "").replace("llc", "").replace(" ", "")
    
    # Сравниваем имя домена и название организации
    if org_name == domain:
        return "10 out of 10"
    elif org_name != "" and org_name != "данные об организации закрыты!":
        return "5 out of 10"
    else:
        return "2 out of 10"



def get_data(url):

    # Отправляем GET-запрос к указанному URL и получаем содержимое страницы
    response = requests.get(url=url, headers=headers)
    src = response.text

    # Создаем объект BeautifulSoup для парсинга HTML-кода
    soup = BeautifulSoup(src, 'lxml')

    # Находим блок с информацией о домене
    table = soup.find('pre', 'raw-domain-info-pre')
    
    if table is None:
        return {'url': input_url, 'error': 'Не удалось получить данные о домене.'}

    # Получаем текст из объекта BeautifulSoup и удаляем пробелы в начале и конце строки
    table_text = table.text.strip()

    # Ищем строку с информацией об организации
    org_info = find_org_string(table_text)

    result = compare_domain_and_organization(domain_name, org_info)

    # Возвращаем результаты выполнения функции в виде словаря
    return {'url': input_url, 'domain': domain_name, 'org_info': org_info.replace("org: ", ""), 'result': result}



def main():
    # Вызываем функцию get_data() для получения данных о домене
    data = get_data(url)

    # Выводим результаты на экран
    print(f"URL: {data['url']}")
    if 'error' in data:
        print('Домен: Имя домена не найдено! \nСоответствие: 0 из 10')
        return
    print(f"Домен: {data['domain']}")
    print(f"Организация: {data['org_info']}")
    print(f"Сравнение домена и названия организации: {data['result']}")



if __name__ == "__main__":
    main()