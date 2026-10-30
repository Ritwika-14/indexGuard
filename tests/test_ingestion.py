def valid_record(**overrides):
    record = {
        "ticker": "AAPL",
        "company_name": "Apple Inc.",
        "price": 189.25,
        "market_cap": 2850000000000,
        "weight": 0.045,
    }
    record.update(overrides)
    return record


def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_database_health_endpoint(client):
    response = client.get("/health/db")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "database": "connected",
    }


def test_create_batch_accepts_valid_records(client):
    response = client.post(
        "/api/v1/ingestion/batches",
        json={
            "source_filename": "sample.json",
            "records": [
                valid_record(),
                valid_record(
                    ticker="MSFT",
                    company_name="Microsoft Corporation",
                    price=420.50,
                ),
            ],
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["records_received"] == 2
    assert data["records_accepted"] == 2
    assert data["records_rejected"] == 0
    assert data["status"] == "completed"
    assert data["batch_id"] > 0


def test_create_batch_rejects_invalid_price(client):
    response = client.post(
        "/api/v1/ingestion/batches",
        json={
            "records": [
                valid_record(price=-10),
                valid_record(
                    ticker="MSFT",
                    company_name="Microsoft Corporation",
                ),
            ],
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["records_received"] == 2
    assert data["records_accepted"] == 1
    assert data["records_rejected"] == 1
    assert data["rejected_records"][0]["record_number"] == 1


def test_create_batch_rejects_duplicate_tickers(client):
    response = client.post(
        "/api/v1/ingestion/batches",
        json={
            "records": [
                valid_record(),
                valid_record(
                    ticker="aapl",
                    company_name="Apple Inc. Duplicate",
                ),
            ],
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["records_accepted"] == 1
    assert data["records_rejected"] == 1
    assert "Duplicate ticker" in (data["rejected_records"][0]["errors"][0])


def test_get_batch_returns_saved_records(client):
    create_response = client.post(
        "/api/v1/ingestion/batches",
        json={"records": [valid_record()]},
    )

    batch_id = create_response.json()["batch_id"]

    response = client.get(f"/api/v1/ingestion/batches/{batch_id}")

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == batch_id
    assert data["records_accepted"] == 1
    assert len(data["constituents"]) == 1
    assert data["constituents"][0]["ticker"] == "AAPL"


def test_get_missing_batch_returns_404(client):
    response = client.get("/api/v1/ingestion/batches/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == ("Ingestion batch 999999 was not found")


def test_empty_batch_is_rejected_by_request_validation(client):
    response = client.post(
        "/api/v1/ingestion/batches",
        json={"records": []},
    )

    assert response.status_code == 422
