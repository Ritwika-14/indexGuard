def make_record(ticker, weight):
    return {
        "ticker": ticker,
        "company_name": f"{ticker} Corporation",
        "price": 100,
        "market_cap": 1_000_000_000,
        "weight": weight,
    }


def test_complete_batch_with_weights_totaling_100_percent(client):
    response = client.post(
        "/api/v1/ingestion/batches",
        json={
            "is_complete": True,
            "records": [
                make_record("AAA", 0.40),
                make_record("BBB", 0.60),
            ],
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["records_accepted"] == 2
    assert data["records_rejected"] == 0
    assert data["status"] == "completed"


def test_complete_batch_with_incorrect_total_is_rejected(client):
    response = client.post(
        "/api/v1/ingestion/batches",
        json={
            "is_complete": True,
            "records": [
                make_record("AAA", 0.40),
                make_record("BBB", 0.40),
            ],
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["records_accepted"] == 0
    assert data["records_rejected"] == 2
    assert data["status"] == "failed"
    assert len(data["rejected_records"]) == 2


def test_partial_batch_does_not_require_weights_to_total_100_percent(client):
    response = client.post(
        "/api/v1/ingestion/batches",
        json={
            "is_complete": False,
            "records": [
                make_record("AAA", 0.20),
                make_record("BBB", 0.30),
            ],
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["records_accepted"] == 2
    assert data["records_rejected"] == 0
    assert data["status"] == "completed"
