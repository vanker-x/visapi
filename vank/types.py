import typing as t

HTTPMethod = t.Literal["GET", "POST", "PUT", "DELETE", "HEAD", "PATCH", "OPTIONS", "TRACE"]

HTTPStatus = t.Tuple[int, str]

