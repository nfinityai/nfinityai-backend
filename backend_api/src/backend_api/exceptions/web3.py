
class Web3Exception(Exception):
    pass

class Web3EventNotFoundInABIException(Web3Exception):
    pass


class Web3UnableToDetermineBlock(Web3Exception):
    pass