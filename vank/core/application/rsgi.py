from vank.core.application.base import Router, MiddlewareMixin


class RSGIApplication(Router, MiddlewareMixin):
    def __call__(self, scope, protocol):
        """
        This is RSGI application entrypoint
        https://github.com/emmett-framework/granian/blob/master/docs/spec/RSGI.md
        :param scope: Which is a dict containing details about the specific connection.
        :param protocol: HTTP protocol object implements two awaitable methods to receive the request body,
        and five different methods to send data, in particular:
        * __call__ to receive the entire body in bytes format
        * __aiter__ to receive the body in bytes chunks
        * response_empty to send back an empty response
        * response_str to send back a response with a str body
        * response_bytes to send back a response with bytes body
        * response_file to send back a file response (from its path)
        * response_stream to start a stream response
        :return:
        """
        assert scope.proto == 'http'

        protocol.response_str(
            status=200,
            headers=[
                ('content-type', 'text/plain')
            ],
            body="Hello, world!"
        )
