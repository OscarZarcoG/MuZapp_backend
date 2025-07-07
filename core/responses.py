# core/responses.py
from rest_framework.response import Response
from rest_framework import status


class BaseSuccessResponse:
    def __init__(self, message=None, data=None):
        self.message = message if message else "Operation successful"
        self.data = data
        self.status_code = status.HTTP_200_OK

    def to_dict(self):
        response = {"message": self.message}
        if self.data:
            response["data"] = self.data
        return response

    def to_response(self):
        return Response(self.to_dict(), status=self.status_code)