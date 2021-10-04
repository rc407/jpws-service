import logging, requests, redis , os 
from flask.helpers import make_response
from flask import Flask, jsonify, request, Response, abort
from prometheus_flask_exporter import PrometheusMetrics
from werkzeug.exceptions import HTTPException
from time import strftime

OSS_REDIS_URL = os.environ['REDIS_URL']
JPWS_FILE_EXT_URL = os.environ['JPWS_FILE_EXT_URL']
JPWS_REDIS_KEY = os.environ['JPWS_REDIS_KEY']
LOG_LEVEL = os.environ['JPWS_LOG_LEVEL']
HEADER_CONTENT_TYPE = "text/plain;charset=UTF-8"
HEADER_CONTENT_DISPOSITION = "attachment;filename=jpws.txt"

# Using default logging for now
logging.basicConfig(level=logging.getLevelName(LOG_LEVEL))
logging.info("Setting LOGLEVEL to " + LOG_LEVEL)

# TO DO: Refactor, better error handling and logging
# Instantiates a redis client for caching
try:
    redis_client = redis.from_url(OSS_REDIS_URL)
    redis_available = True
except Exception as ex:
    logging.debug(ex)
    redis_available = False

logging.debug("Redis connection is available: " + str(redis_available))

api = Flask(__name__)
metrics = PrometheusMetrics(api)
metrics.info("app_info", "JPWS", version="1.0.0")

# This could be a GET with Query string but using POST as per the requirement
@api.route('/manage_file/', methods=['POST'])
def manage_file():
    action_data = request.json.get('action')
    if action_data == 'download' or action_data == 'read':
        logging.debug("action_data: " + action_data)
        try:
            cache_hit = False
            if redis_available:
                if redis_client.exists(JPWS_REDIS_KEY):
                    jpws_file = redis_client.get(JPWS_REDIS_KEY)
                    cache_hit = True
                    logging.debug("Cache hit for key: " + JPWS_REDIS_KEY)

            if not cache_hit:
                logging.debug("Cache not hit. Retrieving and storing information.")
                jpws_file = requests.get(JPWS_FILE_EXT_URL, timeout=5.0)
                jpws_file.raise_for_status()
                jpws_file = jpws_file.content
                if redis_available:
                    redis_client.set(JPWS_REDIS_KEY, jpws_file)
                    
            response = make_response(jpws_file)
            response.headers['Content-Type'] = HEADER_CONTENT_TYPE
            if action_data == 'download':
                response.headers['Content-Disposition'] = HEADER_CONTENT_DISPOSITION

            return response
        except requests.exceptions.RequestException as ex:
            raise Exception(ex)
    else:
        abort(400, "Invalid Payload")

# For service health check
@api.route('/health', methods=['GET'])
@metrics.do_not_track()
def health():
    return "{'health': 'true'}", 200

#Reports error code and full message if HTTP exception otherwise default message with error code 500
@api.errorhandler(Exception)
def handle_error(e):
    timestamp = strftime('[%Y-%b-%d %H:%M]')
    logging.error('%s %s %s %s %s', timestamp, request.remote_addr, request.method, request.scheme, request.full_path)
    logging.error(e)
    return jsonify(error="Internal Server error."), 500

if __name__ == "__main__":
    from waitress import serve
    serve(api, host="0.0.0.0", port=5000)