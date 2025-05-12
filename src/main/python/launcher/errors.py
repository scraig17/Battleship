

class AuthenticationRequiredError(Exception):

    def __init__(self) -> None:
        super().__init__("Must specify authentication credential")
