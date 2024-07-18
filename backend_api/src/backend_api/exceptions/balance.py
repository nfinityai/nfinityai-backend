class BalanceNotFoundError(BaseException):
    pass


class InsufficientFundsError(BaseException):
    pass


class TransactionFailedError(BaseException):
    pass

class TransactionUncompletedError(BaseException):
    pass
