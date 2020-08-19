from django.http import JsonResponse


def test_cors(request):

    res = {'data':{},'code':200}
    return JsonResponse(res)