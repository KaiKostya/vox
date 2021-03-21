import pytest
from connect import Connect
from clients import clients
from items import items
import time
from datetime import datetime, timedelta
CLIENTS = clients
ITEMS = items
skip_marker = False
connect = Connect()

def if_skip_all(statement):
    global skip_marker
    if not statement:
        skip_marker = True

@pytest.fixture(scope="class", autouse=True)
def prepare():
    connect.db_connect("DELETE FROM \"ClientCard\";")
    connect.db_connect("DELETE FROM \"Order\";")
    connect.orders = {}
    yield

def test_create_clients():
    for client in CLIENTS:
        connect.create_client(client)
        if_skip_all(connect.response.status_code == 200)
        assert connect.response.status_code == 200
        if_skip_all(connect.response.json()["isSuccess"] == True)
        assert connect.response.json()["isSuccess"] == True
        if_skip_all(connect.response.json()["errorMessage"] == None)
        assert connect.response.json()["errorMessage"] == None

@pytest.mark.skipif(skip_marker)
class TestNegative:
    @pytest.mark.parametrize("params", [pytest.param({123, ["aaa"]}, id="wrong_client_id"),
    pytest.param({"123", {"aaa": 123}}, id="items_as_dict"),
    pytest.param({"123", ["aaa", 123]}, id="wrong_item")])
    def test_Purchase_By_Client_wrong_type(self, params):
        connect.purchase_ByClient(params)
        connect.print_request(connect.response.request)
        connect.print_response(connect.response)
        assert connect.response.status_code == 400  # Bad request

    @pytest.mark.parametrize("params", [pytest.param({"123", []}, id="empty_items"),
    pytest.param({"", ["aaa"]}, id="empty_client_id")])
    def test_Purchase_By_Client_empty_param(self, params):
        connect.purchase_ByClient(params)
        connect.print_request(connect.response.request)
        connect.print_response(connect.response)
        assert connect.response.status_code == 200
        assert connect.response.json()["isSuccess"] == False
        assert connect.response.json()["errorMessage"] == "Некорректный запрос"

    def test_Purchase_By_Client_Resource_not_Found(self):
        params = {"123", ["123"]}        
        connect.purchase_ByClient(params)
        connect.print_request(connect.response.request)
        connect.print_response(connect.response)
        assert connect.response.status_code == 404  # Not found

@pytest.mark.skipif(skip_marker)
class TestCreate10Orders:
    def test_create_orders(self):
        order = connect.clients[0]
        order["items"] = [ITEMS[0]]
        order["items"][0]["quantity"] = 10
        connect.create_order(order)
        connect.assertSuccess()

    def test_Purchase_by_client_Response_Success(self):
        params = {}
        params["client_id"] = connect.clients[0]["client_id"]
        params["item_ids"] = [ITEMS[0]]
        connect.purchase_ByClient(params)
        connect.assertSuccess()

    @pytest.mark.parametrize("fact, expected", [pytest.param("item_id", 1, id="item_id"),
    pytest.param("purchased", True, id="purchased"),
    pytest.param("purchase_count", 10, id="purchase_count")])
    def test_check_Purchase_by_client_result_key_values(self, fact, expected):
        assert connect.response.json()["result"][fact] == expected

    def test_check_Purchase_by_client_last_order_number(self):
        client_id = connect.clients[0]["client_id"]
        assert connect.response.json()["result"]["last_order_number"] == connect.orders[client_id][1]["last_order_number"]

    def test_check_last_purchase_date(self):
        last_purchase_date = datetime.strptime(connect.response.json()["result"]["last_purchase_date"], "%Y-%m-%dT%H:%M:%S.%fZ")
        client_id = connect.clients[0]["client_id"]
        assert abs((last_purchase_date - connect.orders[client_id][1]["last_purchase_date"]).total_seconds()) < 2

    def test_check_purchase_count(self):
        connect.response.json()["result"]["purchase_count"] == 10

@pytest.mark.skipif(skip_marker)
class TestCreateOrders10Times:
    def test_create_orders_Client_Tom(self):
        order = connect.clients[0]
        for i in range(0,10):
            order["items"] = [ITEMS[i]]
            connect.create_order(order)
            connect.assertSuccess()

    def test_create_orders_Client_Bob(self):
        order = connect.clients[1]
        for i in range(10,15):
            order["items"] = [ITEMS[i]]
            connect.create_order(order)
            connect.assertSuccess()

    def test_Purchase_by_client_Tom_Response_Success(self):
        params = {}
        params["client_id"] = connect.clients[0]["client_id"]
        params["item_ids"] = [ITEMS[5:15]]
        connect.purchase_ByClient(params)
        connect.assertSuccess()

    def test_check_items_Tom_purchased(self):
        for item in connect.response.json()["result"]:
            if item["item_id"] in range(5,10):
                assert item["purchased"] == True
            else:
                assert item["purchased"] == False

    def test_check_last_order_number_Tom(self):
        for item in connect.response.json()["result"]:
            if item["item_id"] in range(5,10):
                client_id = connect.clients[0]["client_id"]
                assert item["last_order_number"] == connect.orders[client_id][item["item_id"]]["last_order_number"]
            else:
                assert item["last_order_number"] == None

    def test_check_last_purchase_date_Tom(self):
        for item in connect.response.json()["result"]:
            if item["item_id"] in range(5,10):
                last_purchase_date = datetime.strptime(item["last_purchase_date"], "%Y-%m-%dT%H:%M:%S.%fZ")
                client_id = connect.clients[0]["client_id"]
                assert abs((connect.orders[client_id][item["item_id"]]["last_purchase_date"] - last_purchase_date).total_seconds()) < 2
            else:
                item["last_purchase_date"] == None

    def test_check_purchase_count_Tom(self):
        for item in connect.response.json()["result"]:
            if item["item_id"] in range(5,10):
                assert item["purchase_count"] == 1
            else:
                assert item["last_order_number"] == 0

    def test_Purchase_by_client_Bob_Response_Success(self):
        params = {}
        params["client_id"] = connect.clients[1]["client_id"]
        params["item_ids"] = [ITEMS[5:15]]
        connect.purchase_ByClient(params)
        connect.assertSuccess()

    def test_check_items_Bob_purchased(self):
        for item in connect.response.json()["result"]:
            if item["item_id"] in range(10,15):
                assert item["purchased"] == True
            else:
                assert item["purchased"] == False

    def test_check_last_order_number_Bob(self):
        for item in connect.response.json()["result"]:
            if item["item_id"] in range(10,15):
                client_id = connect.clients[1]["client_id"]
                assert item["last_order_number"] == connect.orders[client_id][item["item_id"]]["last_order_number"]
            else:
                assert item["last_order_number"] == None

    def test_check_last_purchase_date_Bob(self):
        for item in connect.response.json()["result"]:
            if item["item_id"] in range(10,15):
                client_id = connect.clients[1]["client_id"]
                last_purchase_date = datetime.strptime(item["last_purchase_date"], "%Y-%m-%dT%H:%M:%S.%fZ")
                assert abs((connect.orders[client_id][item["item_id"]]["last_purchase_date"] - last_purchase_date).total_seconds()) < 2
            else:
                item["last_purchase_date"] == None

    def test_check_purchase_count_Bob(self):
        for item in connect.response.json()["result"]:
            if item["item_id"] in range(10,15):
                assert item["purchase_count"] == 1
            else:
                assert item["last_order_number"] == 0

    def test_Purchase_by_client_Mark_Response_Success(self):
        params = {}
        params["client_id"] = connect.clients[2]["client_id"]
        params["item_ids"] = [ITEMS[5:15]]
        connect.purchase_ByClient(params)
        connect.assertSuccess()

    def test_check_items_Mark_purchased(self):
        for item in connect.response.json()["result"]:
            assert item["purchased"] == False

    def test_check_last_order_number_Mark(self):
        for item in connect.response.json()["result"]:
            assert item["last_order_number"] == None

    def test_check_last_purchase_date_Mark(self):
        for item in connect.response.json()["result"]:
            item["last_purchase_date"] == None

    def test_check_purchase_count_Mark(self):
        for item in connect.response.json()["result"]:
            item["purchase_count"] == 0

@pytest.mark.skipif(skip_marker)
class TestCreateOneOrderBy3Clients:
    def test_create_order_By_3_Clients(self):
        for client in CLIENTS:
            order = client
            order["items"] = [ITEMS[19]]
            connect.create_order(order)
            connect.assertSuccess()

    def test_Purchase_by_client_Tom_Response_Success(self):
        params = {}
        params["client_id"] = connect.clients[0]["client_id"]
        params["item_ids"] = [ITEMS[19]]
        connect.purchase_ByClient(params)
        connect.assertSuccess()

    def test_check_item_Tom_purchased(self):
        assert connect.response.json()["result"][0]["purchased"] == True

    def test_check_last_order_number_Tom(self):
        item = connect.response.json()["result"][0]
        client_id = connect.clients[0]["client_id"]
        assert item["last_order_number"] == connect.orders[client_id][item["item_id"]]["last_order_number"]

    def test_check_last_purchase_date_Tom(self):
        item = connect.response.json()["result"][0]
        last_purchase_date = datetime.strptime(item["last_purchase_date"], "%Y-%m-%dT%H:%M:%S.%fZ")
        client_id = connect.clients[0]["client_id"]
        assert abs((connect.orders[client_id][item["item_id"]]["last_purchase_date"] - last_purchase_date).total_seconds()) < 2

    def test_check_purchase_count_Tom(self):
        assert connect.response.json()["result"][0]["purchase_count"] == 1

    def test_Purchase_by_client_Bob_Response_Success(self):
        params = {}
        params["client_id"] = connect.clients[1]["client_id"]
        params["item_ids"] = [ITEMS[19]]
        connect.purchase_ByClient(params)
        connect.assertSuccess()

    def test_check_item_Bob_purchased(self):
        assert connect.response.json()["result"][0]["purchased"] == True

    def test_check_last_order_number_Bob(self):
        item = connect.response.json()["result"][0]
        client_id = connect.clients[1]["client_id"]
        assert item["last_order_number"] == connect.orders[client_id][item["item_id"]]["last_order_number"]

    def test_check_last_purchase_date_Bob(self):
        item = connect.response.json()["result"][0]
        last_purchase_date = datetime.strptime(item["last_purchase_date"], "%Y-%m-%dT%H:%M:%S.%fZ")
        client_id = connect.clients[1]["client_id"]
        assert abs((connect.orders[client_id][item["item_id"]]["last_purchase_date"] - last_purchase_date).total_seconds()) < 2

    def test_check_purchase_count_Bob(self):
        assert connect.response.json()["result"][0]["purchase_count"] == 1

    def test_Purchase_by_client_Mark_Response_Success(self):
        params = {}
        params["client_id"] = connect.clients[2]["client_id"]
        params["item_ids"] = [ITEMS[19]]
        connect.purchase_ByClient(params)
        connect.assertSuccess()

    def test_check_item_Mark_purchased(self):
        assert connect.response.json()["result"][0]["purchased"] == True

    def test_check_last_order_number_Mark(self):
        item = connect.response.json()["result"][0]
        client_id = connect.clients[2]["client_id"]
        assert item["last_order_number"] == connect.orders[client_id][item["item_id"]]["last_order_number"]

    def test_check_last_purchase_date_Mark(self):
        item = connect.response.json()["result"][0]
        last_purchase_date = datetime.strptime(item["last_purchase_date"], "%Y-%m-%dT%H:%M:%S.%fZ")
        client_id = connect.clients[2]["client_id"]
        assert abs((connect.orders[client_id][item["item_id"]]["last_purchase_date"] - last_purchase_date).total_seconds()) < 2

    def test_check_purchase_count_Mark(self):
        assert connect.response.json()["result"][0]["purchase_count"] == 1

class TestCreateOneOrderPeriodically:
    def test_create_order_Periodically_By_Tom(self):
        order = connect.clients[0]
        for i in range(0,10):
            order["items"] = [ITEMS[24]]
            connect.create_order(order)
            connect.assertSuccess()
            time.sleep(2)

    def test_Purchase_by_client_Tom_Response_Success(self):
        params = {}
        params["client_id"] = connect.clients[0]["client_id"]
        params["item_ids"] = [ITEMS[24]]
        connect.purchase_ByClient(params)
        connect.assertSuccess()

    def test_check_item_Tom_purchased(self):
        assert connect.response.json()["result"][0]["purchased"] == True

    def test_check_last_order_number_Tom(self):
        item = connect.response.json()["result"][0]
        client_id = connect.clients[0]["client_id"]
        assert item["last_order_number"] == connect.orders[client_id][item["item_id"]]["last_order_number"]

    def test_check_last_purchase_date_Tom(self):
        item = connect.response.json()["result"][0]
        last_purchase_date = datetime.strptime(item["last_purchase_date"], "%Y-%m-%dT%H:%M:%S.%fZ")
        client_id = connect.clients[0]["client_id"]
        assert abs((connect.orders[client_id][item["item_id"]]["last_purchase_date"] - last_purchase_date).total_seconds()) < 2

    def test_check_purchase_count_Tom(self):
        assert connect.response.json()["result"][0]["purchase_count"] == 10

