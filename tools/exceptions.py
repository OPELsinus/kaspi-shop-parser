class BusinessException(Exception):
    """Exception raised for business rule violations."""

    def __init__(self, message, function_name='', data=None):
        self.message = message
        self.function_name = function_name
        self.data = data


class ApplicationException(Exception):
    """Exception raised for application errors."""

    def __init__(self, message, function_name='', data=None):
        self.message = message
        self.function_name = function_name
        self.data = data


class RobotException(Exception):
    """Unexpected exceptions."""

    def __init__(self, message, function_name='', data=None):
        self.message = message
        self.function_name = function_name
        self.data = data
