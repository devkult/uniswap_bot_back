from dataclasses import dataclass


@dataclass
class ApplicationError(Exception):
    pass

@dataclass
class FetchingPoolsError(ApplicationError):
    message: str

