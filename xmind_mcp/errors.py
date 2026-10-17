"""Domain errors and the public response boundary."""
from functools import wraps
import logging

logger = logging.getLogger(__name__)


class XMindError(Exception):
    def __init__(self, message, code="invalid_input", suggestion=None):
        super().__init__(message)
        self.code = code
        self.suggestion = suggestion

    def as_result(self):
        result = {"status": "error", "message": str(self), "error_code": self.code}
        if self.suggestion:
            result["suggestion"] = self.suggestion
        return result


def result_boundary(fn):
    """Internal code raises; public service calls retain the existing JSON contract."""
    @wraps(fn)
    def call(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except XMindError as exc:
            return exc.as_result()
        except (ValueError, TypeError) as exc:
            return XMindError(str(exc)).as_result()
        except OSError as exc:
            return XMindError(str(exc), "file_error").as_result()
        except Exception:
            logger.exception("XMind operation failed")
            return XMindError("操作失败，请查看服务器日志", "internal_error").as_result()
    return call
