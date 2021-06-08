# Works only from PYTHONEVERYWHERE
import requests
import mysql.connector
import sys

IFTTT_WEBHOOKS_URL = 'https://maker.ifttt.com/trigger/{}/with/key/cGaSSekD3P4cB1dOYu7Ud3ZmwKVgckQHYmujdddKBmC'

payload_to = {
    "flightList":[
        {
            "departureStation": "WRO",
            "arrivalStation": "IEV",
            "departureDate": "2018-11-23"
        }
    ],
    "adultCount": 1,
    "childCount": 0,
    "infantCount": 0,
    "wdc": True,
    "dayInterval": 0
}

payload_from = {
    "flightList":[
        {
            "departureStation": "IEV",
            "arrivalStation": "WRO",
            "departureDate": "2018-11-26"
        }
    ],
    "adultCount": 1,
    "childCount": 0,
    "infantCount": 0,
    "wdc": True,
    "dayInterval": 0
}

url = 'https://be.wizzair.com/8.4.0/Api/search/search'


def return_ticket_price():
    try:
        r_to = requests.post(url, json=payload_to)
        r_from = requests.post(url, json=payload_from)
        r_to.raise_for_status()
        r_from.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
        err_list = list((str(err)).split())
        err_final = err_list[0:5]
        err_return = ' '.join(err_final)
        post_ifttt_webhook('wizz_air_price', err_return)
        sys.exit(1)

    data_to = r_to.json()
    data_from = r_from.json()

    flight_price_to = (data_to['outboundFlights'][0]['fares'][3]['discountedPrice']['amount'])
    destination_to = (data_to['outboundFlights'][0]['departureStation']) + '-' + (
    data_to['outboundFlights'][0]['arrivalStation'])
    ret_tup_to = (int(flight_price_to), destination_to)

    flight_price_from = (data_from['outboundFlights'][0]['fares'][3]['discountedPrice']['amount'])
    destination_from = (data_from['outboundFlights'][0]['departureStation']) + '-' + (
    data_from['outboundFlights'][0]['arrivalStation'])

    ret_tup_from = (int(flight_price_from * 0.136), destination_from)

    ret_tup = (ret_tup_to, ret_tup_from)
    #print(ret_tup)
    return ret_tup


def post_ifttt_webhook(event, value):
    data = {'value1': value}  # The payload that will be sent to IFTTT service
    ifttt_event_url = IFTTT_WEBHOOKS_URL.format(event)  # Inserts our desired event
    requests.post(ifttt_event_url, json=data)


def main():
    data_tuple = return_ticket_price()
    float_price_ticket_to = data_tuple[0][0]
    float_price_ticket_from = data_tuple[1][0]
    price_wizz = 'Ticket ' + data_tuple[0][1] + ' is: ' + str(data_tuple[0][0]) + '\n' + 'Ticket ' + data_tuple[1][1] + ' is: ' + str(data_tuple[1][0])
    #print(price_wizz)

    if float_price_ticket_to <= 120:
        post_ifttt_webhook('wizz_air_price', price_wizz)

    dest_to = str(data_tuple[0][1])
    dest_from = str(data_tuple[1][1])

    #print(type(float_price_ticket_to), type(float_price_ticket_from))

    connection = mysql.connector.connect(
        user='XXXXXX', password='XXXXXX',
        host='XXXXXX.mysql.pythonanywhere-services.com',port=3306, database='XXXXXX$test_db'
    )

    cursor = connection.cursor(buffered=True)
    cursor.execute("INSERT INTO WIZZ (DIRECTION, PRICE) VALUES (%s, %s)",
                   (dest_to, float_price_ticket_to))
    cursor.execute("INSERT INTO WIZZ (DIRECTION, PRICE) VALUES (%s, %s)",
                   (dest_from, float_price_ticket_from))
    cursor.execute("SELECT ID, DATE_FORMAT(BSNSS_DT, '%d-%m-%Y' ) AS DATE, DIRECTION, PRICE FROM airmax$test_db.WIZZ ORDER BY ID DESC LIMIT 2")
    rows = cursor.fetchall()
    print(rows)

    connection.commit()
    cursor.close()
    connection.close()


if __name__ == '__main__':
    main()
