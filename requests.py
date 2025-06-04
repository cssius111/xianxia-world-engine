class Response:
    def __init__(self, status_code=200, json_data=None):
        self.status_code = status_code
        self._json_data = json_data or {"choices": [{"message": {"content": ""}}]}
    def json(self):
        return self._json_data


def post(*args, **kwargs):
    return Response()
