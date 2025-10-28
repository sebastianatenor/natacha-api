from flask import jsonify

def json_response(data, status=200):
    """
    Devuelve una respuesta JSON estándar.
    """
    response = jsonify(data)
    response.status_code = status
    return response
