import json


class Message:
    def __init__(self, server_id: str, request_id: str, method_name: str, params: dict):
        self.server_id = server_id
        self.request_id = request_id
        self.method_name = method_name
        self.params = params

    def toJson(self):
        return json.dumps(self.__dict__)

    @staticmethod
    def fromJson(json_str: str):
        json_dict = json.loads(json_str)
        return Message(**json_dict)


class OutgoingMessage:
    def __init__(self, server_id: str, request_id: str, bool_result: bool, result: str):
        self.server_id = server_id
        self.request_id = request_id
        self.bool_result = bool_result
        self.result = result

    def toJson(self):
        return json.dumps(self.__dict__)

    @staticmethod
    def fromJson(json_str: str):
        json_dict = json.loads(json_str)
        return OutgoingMessage(**json_dict)
