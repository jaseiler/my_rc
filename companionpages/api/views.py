import base64
import datetime
import hmac
import sha

from django.conf import settings

from dateutil.tz import tzlocal
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from lib.storage import upload_path


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def s3signatures(request):
    """ Return a signature so that files can be uploaded to the s3 materials bucket """

    if 's3_object_name' not in request.QUERY_PARAMS:
        return Response({"message": "missing s3_object_name from request"}, status=status.HTTP_400_BAD_REQUEST)

    s3name = upload_path(request.user.username, request.QUERY_PARAMS['s3_object_name'])
    # Canonical strings and key signing are documented in the s3 developer guide.
    # http://s3.amazonaws.com/doc/s3-developer-guide/RESTAuthentication.html
    amz_date = datetime.datetime.now(tzlocal()).strftime('%a, %d %b %Y %H:%M:%S %Z')
    canonical_string = "POST\n\n\nx-amz-date:{}\n{}".format(amz_date, s3name)
    h = hmac.new(settings.AWS_SECRET_ACCESS_KEY, canonical_string, sha)
    signature = base64.encodestring(h.digest()).strip()

    return Response({
        'signed_request': signature,
        'url': s3name,
        'key_id': settings.AWS_ACCESS_KEY_ID,
        'x-amz-date': amz_date,
        'canonical_string': canonical_string,
        'Authorization': 'AWS {}:{}'.format(settings.AWS_ACCESS_KEY_ID, signature),
    })