import requests
from bs4 import BeautifulSoup
import mysql.connector

import pandas as pd

pd.set_option('display.max_columns', None)
MAX_PAGES = 10


def fetch_cars_data():
    cnx = mysql.connector.connect(user='saeideh', password='',
                                  host='localhost',
                                  database='jadi_project_db')
    cursor = cnx.cursor()

    cursor.execute("SELECT * FROM true_car_items;")

    df = pd.DataFrame(cursor.fetchall())
    df.columns = cursor.column_names
    cnx.commit()

    return df


def insert_to_db(cars_info):
    cnx = mysql.connector.connect(user='saeideh', password='',
                                  host='localhost',
                                  database='jadi_project_db')
    cursor = cnx.cursor()

    for item in cars_info.items():
        car = item[1]
        sql = "INSERT IGNORE INTO true_car_items (name, year, style, exterior_color, interior_color, mpg, engine, " \
              "drive_type, fuel_type, transmission, price) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        val = list(str(i) for i in car.values())
        cursor.execute(sql, val)
    cnx.commit()


def delete_duplicate_rows():
    cnx = mysql.connector.connect(user='saeideh', password='',
                                  host='localhost',
                                  database='jadi_project_db')
    cursor = cnx.cursor()

    sql = "DELETE t1 FROM true_car_items t1 INNER JOIN true_car_items t2 WHERE t1.id > t2.id AND t1.name = t2.name " \
          "AND t1.year = t2.year AND t1.drive_type = t2.drive_type AND t1.transmission = t2.transmission AND t1.price " \
          "= t2.price; "

    cursor.execute(sql)
    cnx.commit()


def crawl_true_car_data():
    base_url = 'https://www.truecar.com'
    info = {}
    num_items = 0
    for i in range(1, MAX_PAGES + 1):

        res = requests.get(base_url + '/new-cars-for-sale/listings/' + f'?page={i}',
                           headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(res.text, 'html.parser')

        for item in soup.findAll('div', attrs={'class': 'linkable card card-shadow vehicle-card'}):
            more_info_link = item.find('a', href=True)
            detail_url = base_url + more_info_link['href']

            res = requests.get(detail_url, headers={'User-Agent': 'Mozilla/5.0'})
            detail_soup = BeautifulSoup(res.text, 'html.parser')

            vehicle_name = item.find('div', attrs={'class': 'card-content vehicle-card-body order-3'}) \
                .find('div', attrs={'class': 'vehicle-card-top'}) \
                .find('h3', attrs={'class': 'heading-base'}) \
                .find('div', attrs={'class': 'vehicle-card-header w-100'}) \
                .find('span', attrs={'class': 'vehicle-header-make-model text-truncate'})

            vehicle_price = item.find('div', attrs={'class': 'card-content vehicle-card-body order-3'}) \
                .find('div', attrs={'data-test': 'newCarCardPricingSection'}) \
                .find('div', attrs={'class': 'vehicle-card-bottom vehicle-card-bottom-top-spacing'}) \
                .find('div', attrs={'class': 'd-flex w-100 vehicle-card-bottom-pricing justify-content-between'}) \
                .find('div', attrs={'class': 'heading-4 font-weight-bold'}) \
                .find('span', attrs={'class': 'text-truncate'})
            if vehicle_price is None:
                price = 0
            else:
                price = (vehicle_price.text).replace('$', '')
                price = (price).replace(',', '')

            vehicle_year = item.find('div', attrs={'class': 'card-content vehicle-card-body order-3'}) \
                .find('div', attrs={'class': 'vehicle-card-top'}) \
                .find('h3', attrs={'class': 'heading-base'}) \
                .find('div', attrs={'class': 'vehicle-card-header w-100'}) \
                .find('span', attrs={'class': 'vehicle-card-year font-size-1'})

            overview = detail_soup.findAll('div', attrs={'class': 'd-flex flex-column'})

            info.update({num_items: {'name': vehicle_name.text, 'year': vehicle_year.text,
                                     overview[3].find('div').text: overview[3].text,
                                     overview[4].find('div').text: overview[4].find('p').text,
                                     overview[5].find('div').text: overview[5].find('p').text,
                                     overview[6].find('div').text: overview[6].find('p').text,
                                     overview[7].find('div').text: overview[7].find('p').text,
                                     overview[8].find('div').text: overview[8].find('p').text,
                                     overview[9].find('div').text: overview[9].find('p').text,
                                     overview[10].find('div').text: overview[10].find('p').text,
                                     'price': price}
                         })

            num_items += 1
            if num_items == 2:
                return info

    return info


cars_info = crawl_true_car_data()

lst = ['name', 'year', 'Style', 'Exterior Color', 'Interior Color', 'MPG', 'Engine', 'Drive Type', 'Fuel Type',
       'Transmission', 'price']

for car in cars_info.items():
    i = 0
    for key in car[1].keys():
        if key == lst[i]:
            # print(key)
            i += 1
            continue
        else:
            car[1].update({lst[i]: 'Unknown'})
            i += 1


insert_to_db(cars_info)
delete_duplicate_rows()
