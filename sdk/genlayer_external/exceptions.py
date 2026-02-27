class RelayError(Exception):
    pass


class RelaySignatureError(RelayError):
    pass


class RelayResponseError(RelayError):
    pass
