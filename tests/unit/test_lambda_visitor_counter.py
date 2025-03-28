import json
import pytest
from unittest.mock import patch

from lambda_visitor_counter import get_inputs, lambda_handler


expected_payload = ('foo', 'bar')


def create_valid_request():
    return {
        'headers': {},
        'body': json.dumps({'tableName': expected_payload[0], 'primaryKey': expected_payload[1]})
    }
    

def test_valid_payload():
    request = create_valid_request()
    output_payload = get_inputs(request)
    assert output_payload == expected_payload


def test_invalid_payload():
    request = {
        'headers': {}
    }
    with pytest.raises(KeyError):
        get_inputs(request)


def test_invalid_payload_keys():
    request = {
        'headers': {},
        'body': json.dumps({'table_name': expected_payload[0], 'primary_key': expected_payload[1]})
    }
    with pytest.raises(KeyError):
        get_inputs(request)


def test_lambda_handler_for_success():
    expected_counter = 50
    expected_response = {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({'visitorCount': expected_counter})
    }
    with patch("lambda_visitor_counter.get_updated_visitor_counter", return_value=expected_counter):
        response = lambda_handler(create_valid_request(), None)
    print(response)
    assert response == expected_response


def test_lambda_handler_for_failure():
    expected_exception = Exception()
    expected_response = {
        'statusCode': 500,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({'error': str(expected_exception)})
    }
    with patch("lambda_visitor_counter.get_updated_visitor_counter", side_effect=expected_exception):
        response = lambda_handler(create_valid_request(), None)
    assert response == expected_response