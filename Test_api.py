import requests
import pytest
import uuid

BASE_URL = "https://qa-internship.avito.com/api/"

created_item_id = None


@pytest.fixture
def seller_id():
    return 232425601


@pytest.fixture
def item_name():
    return "Andrews"


@pytest.fixture
def item_price():
    return 256


@pytest.fixture
def item_statistics():
    return {"likes": 156, "viewCount": 24, "contacts": 99}


def test_create_ads_valid(seller_id, item_name, item_price, item_statistics):
    global created_item_id
    body = {
        "sellerID": seller_id,
        "name": item_name,
        "price": item_price,
        "statistics": item_statistics,
    }

    response = requests.post(f"{BASE_URL}1/item", json=body)

    assert (
        response.status_code == 200
    ), f"Ожидался 200, получен {response.status_code}. Ответ: {response.text}"
    data = response.json()
    assert "status" in data, "В ответе отсутствует поле 'status'"
    assert data["status"].startswith(
        "Сохранили объявление - "
    ), "Неверный формат status"

    item_id_str = data["status"].split(" - ")[1]
    try:
        uuid.UUID(item_id_str)
    except ValueError:
        pytest.fail(f"ID '{item_id_str}' не является валидным UUID")

    created_item_id = item_id_str
    print(f"Test 1:passed")
    print(f"Создан ID: {created_item_id}")


def test_search_ads_id(seller_id, item_name, item_price, item_statistics):
    response = requests.get(f"{BASE_URL}1/item/{created_item_id}")

    assert (
        response.status_code == 200
    ), f"Ожидался 200, получен {response.status_code}. Ответ: {response.text}"
    data = response.json()
    item = data[0]
    assert item["id"] == created_item_id
    assert item["name"] == item_name
    assert item["price"] == item_price
    assert item["sellerId"] == seller_id
    assert item["statistics"]["contacts"] == item_statistics["contacts"]
    assert item["statistics"]["likes"] == item_statistics["likes"]
    assert item["statistics"]["viewCount"] == item_statistics["viewCount"]
    print(f"Test 2:passed")


def test_search_all_ads_id(seller_id, item_name, item_price, item_statistics):
    response = requests.get(f"{BASE_URL}1/{seller_id}/item")
    assert (
        response.status_code == 200
    ), f"Ожидался 200, получен {response.status_code}. Ответ: {response.text}"
    data = response.json()

    item = None
    for announcement in data:
        if announcement["id"] == created_item_id:
            item = announcement
            break

    assert item is not None, f"Объявление с ID {created_item_id} не найдено в списке"
    assert item["id"] == created_item_id
    assert item["name"] == item_name
    assert item["price"] == item_price
    assert item["sellerId"] == seller_id
    assert item["statistics"]["contacts"] == item_statistics["contacts"]
    assert item["statistics"]["likes"] == item_statistics["likes"]
    assert item["statistics"]["viewCount"] == item_statistics["viewCount"]
    print(f"Test 3:passed")
    print(f"Найдено {len(data)} объявлений пользователя")
    print(response.text)


def test_search_all_ads_id_empty(seller_id):
    response = requests.delete(f"{BASE_URL}2/item/{created_item_id}")
    response = requests.get(f"{BASE_URL}1/{seller_id}/item")
    assert (
        response.status_code == 200
    ), f"Ожидался 200, получен {response.status_code}. Ответ: {response.text}"
    data = response.json()
    assert data == []
    print(f"Test 4:passed")
    print(response.text)


def test_search_statistics_ads_id(seller_id, item_name, item_price, item_statistics):
    global created_item_id
    body = {
        "sellerID": seller_id,
        "name": item_name,
        "price": item_price,
        "statistics": item_statistics,
    }
    response = requests.post(f"{BASE_URL}1/item", json=body)
    data = response.json()
    item_id_str = data["status"].split(" - ")[1]
    created_item_id = item_id_str
    response = requests.get(f"{BASE_URL}1/statistic/{created_item_id}")
    assert (
        response.status_code == 200
    ), f"Ожидался 200, получен {response.status_code}. Ответ: {response.text}"
    data = response.json()
    item = data[0]

    assert item["contacts"] == item_statistics["contacts"]
    assert item["likes"] == item_statistics["likes"]
    assert item["viewCount"] == item_statistics["viewCount"]
    print(f"Test 5:passed")
    print(response.text)


def test_delete_ads_id():
    global created_item_id
    response = requests.delete(f"{BASE_URL}2/item/{created_item_id}")
    assert (
        response.status_code == 200
    ), f"Ожидался 200, получен {response.status_code}. Ответ: {response.text}"
    print(f"Test 6:passed")
    print(response.text)


def test_create_ads_invalid_no_field():
    body = {
        "sellerID": 125149,
        "name": "",
        "price": 255,
        "statistics": {"likes": 156, "viewCount": 24, "contacts": 99},
    }

    response = requests.post(f"{BASE_URL}1/item", json=body)

    assert (
        response.status_code == 400
    ), f"Ожидался 400, получен {response.status_code}. Ответ: {response.text}"
    print(f"Test 7:passed")
    print(response.text)


def test_create_ads_invalid_data():
    global created_item_id
    body = {
        "sellerID": "125149",
        "name": "Andres",
        "price": 255,
        "statistics": {"likes": 156, "viewCount": 24, "contacts": 99},
    }

    response = requests.post(f"{BASE_URL}1/item", json=body)

    assert (
        response.status_code == 400
    ), f"Ожидался 400, получен {response.status_code}. Ответ: {response.text}"
    print(f"Test 8:passed")
    print(response.text)


def test_search_ads_ivalid_id():
    response = requests.get(f"{BASE_URL}1/item/32131")

    assert (
        response.status_code == 400
    ), f"Ожидался 400, получен {response.status_code}. Ответ: {response.text}"
    print(f"Test 9:passed")
    print(response.text)


def test_search_ads_non_existent_id():
    response = requests.get(f"{BASE_URL}1/item/01855daa-7697-450a-97ff-76eb156309cb")
    assert (
        response.status_code == 404
    ), f"Ожидался 404, получен {response.status_code}. Ответ: {response.text}"
    print(f"Test 10:passed")
    print(response.text)


def test_search_all_ads_invalid_id():
    response = requests.get(f"{BASE_URL}1/aw/item")
    assert (
        response.status_code == 400
    ), f"Ожидался 400, получен {response.status_code}. Ответ: {response.text}"
    print(f"Test 11:passed")
    print(response.text)


def test_search_all_ads_negative_id():
    response = requests.get(f"{BASE_URL}1/-1/item")
    assert (
        response.status_code == 200
    ), f"Ожидался 200, получен {response.status_code}. Ответ: {response.text}"
    print(f"Test 12:passed")


def test_search_all_ads_max_min_id():
    response = requests.get(f"{BASE_URL}1/3213213131231231231/item")
    assert (
        response.status_code == 200
    ), f"Ожидался 200, получен {response.status_code}. Ответ: {response.text}"
    print(f"Test 13:passed")
    print(response.text)


def test_search_all_ads_empty_id():
    response = requests.get(f"{BASE_URL}1//item")
    assert (
        response.status_code == 405
    ), f"Ожидался 405, получен {response.status_code}. Ответ: {response.text}"
    print(f"Test 15:passed")
    print(response.text)


def test_search_statistic_ads_non_exist_id():
    response = requests.get(
        f"{BASE_URL}1/statistic/01855daa-7697-450a-97ff-76eb156309c1"
    )
    assert (
        response.status_code == 404
    ), f"Ожидался 404, получен {response.status_code}. Ответ: {response.text}"
    print(f"Test 16:passed")
    print(response.text)


def test_search_statistic_ads_invalid_id():
    response = requests.get(f"{BASE_URL}1/statistic/")
    assert (
        response.status_code == 404
    ), f"Ожидался 404, получен {response.status_code}. Ответ: {response.text}"
    print(f"Test 17:passed")
    print(response.text)


def test_search_statistic_ads_min_max_id():
    response = requests.get(f"{BASE_URL}1/statistic/132131313131313113131231231")
    assert (
        response.status_code == 400
    ), f"Ожидался 400, получен {response.status_code}. Ответ: {response.text}"
    print(f"Test 18:passed")
    print(response.text)


def test_search_statistic_ads_negative_id():
    response = requests.get(f"{BASE_URL}1/statistic/-1")
    assert (
        response.status_code == 400
    ), f"Ожидался 400, получен {response.status_code}. Ответ: {response.text}"
    print(f"Test 19:passed")
    print(response.text)


def test_search_statistic_ads_negative_id():
    response = requests.get(f"{BASE_URL}1/statistic/aw")
    assert (
        response.status_code == 400
    ), f"Ожидался 400, получен {response.status_code}. Ответ: {response.text}"
    print(f"Test 20:passed")
    print(response.text)


def test_delete_ads_non_exist_id():
    response = requests.delete(
        f"{BASE_URL}2/item/01855daa-7697-450a-97ff-76eb156309cb1"
    )
    assert (
        response.status_code == 400
    ), f"Ожидался 400, получен {response.status_code}. Ответ: {response.text}"
    print(f"Test 21:passed")
    print(response.text)


def test_delete_ads_invalid_id():
    response = requests.delete(f"{BASE_URL}2/item/aw")
    assert (
        response.status_code == 400
    ), f"Ожидался 400, получен {response.status_code}. Ответ: {response.text}"
    print(f"Test 22:passed")
    print(response.text)


def test_delete_ads_negative_id():
    response = requests.delete(f"{BASE_URL}2/item/-1")
    assert (
        response.status_code == 400
    ), f"Ожидался 400, получен {response.status_code}. Ответ: {response.text}"
    print(f"Test 23:passed")
    print(response.text)


def test_delete_ads_min_max_id():
    response = requests.delete(f"{BASE_URL}2/item/3213123131313132131313131321")
    assert (
        response.status_code == 400
    ), f"Ожидался 400, получен {response.status_code}. Ответ: {response.text}"
    print(f"Test 24:passed")
    print(response.text)
