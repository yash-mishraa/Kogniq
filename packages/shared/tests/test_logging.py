import json
import logging
from shared.logging.configuration import JSONFormatter
from shared.logging.context import set_telemetry_context, reset_telemetry_context, get_context_logger, TelemetryContextFilter

def test_json_formatter_basic():
    formatter = JSONFormatter()
    record = logging.LogRecord('test_logger', logging.INFO, 'path/to/file.py', 10, 'my event message', (), None)
    record.tool_name = 'search'
    record.duration_ms = 150

    output = formatter.format(record)
    data = json.loads(output)
    
    assert 'timestamp' in data
    assert data['level'] == 'INFO'
    assert data['event'] == 'my event message'
    assert data['tool_name'] == 'search'
    assert data['duration_ms'] == 150

def test_json_formatter_unserializable():
    class Unserializable:
        def __str__(self):
            return "unserializable_str"
            
    formatter = JSONFormatter()
    record = logging.LogRecord('test_logger', logging.INFO, 'path/to/file.py', 10, 'test event', (), None)
    record.bad_field = Unserializable()
    
    output = formatter.format(record)
    data = json.loads(output)
    
    assert data['bad_field'] == "unserializable_str"

def test_telemetry_context_filter():
    token = set_telemetry_context({"request_id": "req-123", "user_id": "usr-456"})
    try:
        f = TelemetryContextFilter()
        record = logging.LogRecord('test_logger', logging.INFO, 'path', 10, 'event', (), None)
        f.filter(record)
        assert record.request_id == "req-123"
        assert record.user_id == "usr-456"
        
        formatter = JSONFormatter()
        data = json.loads(formatter.format(record))
        assert data['request_id'] == "req-123"
        assert data['user_id'] == "usr-456"
    finally:
        reset_telemetry_context(token)

def test_telemetry_isolation():
    token1 = set_telemetry_context({"request_id": "r1"})
    try:
        f = TelemetryContextFilter()
        rec1 = logging.LogRecord('test', logging.INFO, '', 0, '', (), None)
        f.filter(rec1)
        assert rec1.request_id == "r1"
        
        token2 = set_telemetry_context({"request_id": "r2"})
        try:
            rec2 = logging.LogRecord('test', logging.INFO, '', 0, '', (), None)
            f.filter(rec2)
            assert rec2.request_id == "r2"
        finally:
            reset_telemetry_context(token2)
            
        rec3 = logging.LogRecord('test', logging.INFO, '', 0, '', (), None)
        f.filter(rec3)
        assert rec3.request_id == "r1"
    finally:
        reset_telemetry_context(token1)
