import requests, traceback, sys, psycopg2
from datetime import datetime
class Connect:
    def __init__(self):
        self.headers = {"Content-Type": "application/json", "x-date-format": "ISO"}
        self.url =  "http://127.0.0.1:8080/service/v1/"
        self.connect_string = "user = postgres password = 1234 host = 127.0.0.1 port = 5432 dbname = shop"
        self.clients = []
        self.orders = {}

    def db_connect(self, query):
        self.db_result = []
        try:
            connection = psycopg2.connect(self.connect_string)
            cursor = connection.cursor()
            cursor.execute(query)
            if "SELECT" in query:
                for row in cursor.fetchall():
                    self.db_result.append(row)
            connection.commit()
            connection.close()
        except Exception:
            print("Exception while execute query")
            traceback.print_exc(file=sys.stdout)

    def post_request(self, command, params):
        self.response = None
        try:
            self.response = requests.post(self.url + command, headers=self.headers, json=params)
        except Exception:
            print("Exception while making the request:")
            traceback.print_exc(file=sys.stdout)

    def print_request(self, data):
        print( '\n{}\n{}\n\n{}\n\n{}\n'.format(
        '-----------Request----------->',
        data.method + ' ' + data.url,
        '\n'.join('{}: {}'.format(k, v) for k, v in data.headers.items()),
        data.body)
        )

    def print_response(self, data):
        print( '\n{}\n{}\n\n{}\n\n{}\n'.format(
        '-----------Response----------->',
        'Status code:' + str(data.status_code),
        '\n'.join('{}: {}'.format(k, v) for k, v in data.headers.items()),
        data.text)
        )

    def assertSuccess(self):
        self.print_request(self.response.request)
        self.print_response(self.response)
        assert self.response.status_code == 200
        assert self.response.json()["isSuccess"] == True
        assert self.response.json()["errorMessage"] == None
    
    def create_client(self, client):
        self.post_request("client/create", client)
        result = client
        result["client_id"] = self.response.json()["result"]("client_id")
        del result["surname"]
        self.clients.append(result)

    def create_order(self, order):
        self.post_request("order/create", order)
        result = self.response.json()["result"]
        if not order["client_id"] in self.orders.keys():
            self.orders[order["client_id"]] = {}
        for item in order["items"]:                # При создании заказа пишем каждому клиенту набор заказов. Каждый заказ  - это словарь с ключами last_purchase_date и last_order_number
            self.orders[order["client_id"]][item["item_id"]] = {"last_purchase_date": datetime.utcnow(), "last_order_number": result["order_number"]}

    def purchase_ByClient(self, params):
        self.post_request("item/purchase/by-client", params)