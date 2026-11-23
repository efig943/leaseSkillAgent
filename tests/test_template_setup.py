# tests/test_template_setup.py
import json, os

def test_template_config_structure():
    config_path = "template_config.json"
    assert os.path.exists(config_path), "template_config.json must exist"
    with open(config_path) as f:
        config = json.load(f)
    assert "template_doc_id" in config
    assert len(config["template_doc_id"]) > 10
    assert "source_doc_id" in config
