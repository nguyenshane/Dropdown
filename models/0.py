import logging
logger = logging.getLogger("dropdown")
logger.setLevel(logging.DEBUG)


if request.env.http_host:  
    response.headers['Access-Control-Allow-Origin'] = "*"
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Max-Age'] = 86400
    #logger.info(response.headers)

if request.env.request_method == 'OPTIONS':
    if request.env.http_access_control_request_method:
         response.headers['Access-Control-Allow-Methods'] = request.env.http_access_control_request_method
    if request.env.http_access_control_request_headers:
         response.headers['Access-Control-Allow-Headers'] = request.env.http_access_control_request_headers
    raise HTTP(200, **(response.headers)) # not sure about this line