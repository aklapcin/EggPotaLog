import json

from django.http import HttpResponse


def json_response(view):
    """If user is not logger, redirect to login page
    """
    def decorator(request, *args, **kwargs):
        result = view(request, *args, **kwargs)
        code = 200
        if type(result) == dict or type(result) == list:
            if type(result) == dict:
                if result.get('code'):
                    code = result.pop('code')
            data = json.dumps(result)
            return HttpResponse(data, mimetype="application/json", status=code)
        return result

    return decorator
