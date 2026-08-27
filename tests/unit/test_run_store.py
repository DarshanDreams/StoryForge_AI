from src.observability.run_store import RunStore


def test_run_store_filters_recent_records(tmp_path):
    store = RunStore(tmp_path / "runs.jsonl")
    store.append({"run_id": "one", "action": "Plan episode"})
    store.append({"run_id": "two", "action": "Critique screenplay"})

    assert store.recent(1)[0]["run_id"] == "two"
    assert store.compare("Plan episode")[0]["run_id"] == "one"