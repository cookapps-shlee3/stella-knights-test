import os
import signal
import multiprocessing
import sys
import logging
from gunicorn.glogging import Logger
from loguru import logger
from app.config.settings import settings
from app.util.util import is_prod

ENVIRONMENT = os.environ.get('PRODUCTION')

workers_per_core_str = os.getenv("WORKERS_PER_CORE", "1")
web_concurrency_str = os.getenv("WEB_CONCURRENCY", None)

host = "localhost"
port = settings.PORT
# socket과 연결 할때는 다음과 같이 설정하도록 함.
# host = os.getenv("HOST", "unix")
# port = os.getenv("PORT", "///tmp/asgi.sock")
bind_env = os.getenv("BIND", None)
if ENVIRONMENT == 'prod':
    use_loglevel = os.getenv("LOG_LEVEL", "WARNING")
else:
    use_loglevel = os.getenv("LOG_LEVEL", "INFO")
JSON_LOGS = True if os.environ.get("JSON_LOGS", "0") == "1" else False

class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


class StubbedGunicornLogger(Logger):
    def setup(self, cfg):
        handler = logging.NullHandler()
        self.error_logger = logging.getLogger("gunicorn.error")
        self.error_logger.addHandler(handler)
        self.access_logger = logging.getLogger("gunicorn.access")
        self.access_logger.addHandler(handler)
        self.error_logger.setLevel(use_loglevel)
        self.access_logger.setLevel(use_loglevel)


if bind_env:
    use_bind = bind_env
else:
    use_bind = f"{host}:{port}"
cores = multiprocessing.cpu_count()
workers_per_core = float(workers_per_core_str)
default_web_concurrency = workers_per_core * cores + 1
if web_concurrency_str:
    web_concurrency = int(web_concurrency_str)
    assert web_concurrency > 0
else:
    if settings.ENVIRONMENT  == 'dev':
        web_concurrency = 1
    else:
        web_concurrency = max(int(default_web_concurrency), 2)
    
# Gunicorn config variables
loglevel = use_loglevel
workers = web_concurrency
bind = use_bind
keepalive = 120
errorlog = "-"
# For debugging and testing

intercept_handler = InterceptHandler()
logging.root.setLevel(use_loglevel)

seen = set()
for name in [
    *logging.root.manager.loggerDict.keys(),
    "gunicorn",
    "gunicorn.access",
    "gunicorn.error",
    "uvicorn",
    "uvicorn.access",
    "uvicorn.error",
]:
    if name not in seen:
        seen.add(name.split(".")[0])
        logging.getLogger(name).handlers = [intercept_handler]



logger.configure(handlers=[{"sink": sys.stdout, "serialize": JSON_LOGS}])
if settings.ENVIRONMENT  == 'dev':
    logger.add("./logs/log-{time:YYYY-MM-DD}.txt", rotation="00:00", retention="3 days",level=loglevel)
# else:
#     logger.add("./logs/log-{time:YYYY-MM-DD}.txt", rotation="00:00", level=loglevel)

log_data = {
    "loglevel": loglevel,
    "workers": workers,
    "bind": bind,
    # Additional, non-gunicorn variables
    "workers_per_core": workers,
    "logger_class": StubbedGunicornLogger,
    "host": host,
    "port": port,
}

def worker_int(worker):
    os.kill(worker.pid, signal.SIGINT)