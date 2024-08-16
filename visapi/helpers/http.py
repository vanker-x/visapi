from urllib.parse import unquote
from datastructure import FormFile, Form


class ParseException(Exception):
    pass


class MultiPartFormParser:
    def __init__(self, body, boundary):
        self.body = body
        self.boundary = boundary if isinstance(boundary, bytes) else boundary.encode('latin-1')

    async def parse(self) -> Form:
        buffer = b""
        boundary_len = len(self.boundary)
        form = Form()
        async for chunk in self.body:
            buffer += chunk
            start = 0

            while True:
                boundary_start = buffer.find(self.boundary, start)
                if boundary_start == -1:
                    break

                boundary_end = buffer.find(self.boundary, boundary_start + boundary_len)
                if boundary_end == -1:
                    break

                part = buffer[boundary_start + boundary_len:boundary_end]
                header, content = part.split(b"\r\n\r\n", maxsplit=1)
                content = content.strip(b'\r\n')
                headers = dict([line.split(b': ', 1) for line in header.split(b'\r\n')[1:]])
                # https://datatracker.ietf.org/doc/html/rfc7578#section-4.2
                dtype, rest = headers.get(b'Content-Disposition').split(b'; ', 1)
                disposition_parameters = dict(line.split(b'=') for line in rest.split(b'; '))
                disposition_parameters = dict(
                    (key, value.strip(b'"')) for key, value in disposition_parameters.items())
                try:
                    field_name = disposition_parameters[b"name"]
                except KeyError:
                    raise ParseException('The Content Disposition header field "name" must be provided')
                # try to get charset from disposition-parameters and the default is utf-8
                charset = disposition_parameters.get(b'charset', b'utf-8').decode()
                field_name = field_name.decode(charset)
                # if filename in disposition_parameters and that means this part is a file type
                if b"filename" in disposition_parameters.keys():
                    # First, try decoding the file name field prudently
                    # and then try decoding the file name field using UTF-8 if it fails
                    # from https://datatracker.ietf.org/doc/html/rfc8187#section-3.2.1
                    try:
                        f_charset, language, value_chars = disposition_parameters[b"filename*"].split(b"'")
                    except Exception as e:
                        filename = disposition_parameters[b'filename'].decode('utf-8')
                    else:
                        filename = unquote(value_chars, encoding=f_charset.decode())
                        disposition_parameters[b"filename*"] = dict(
                            charset=f_charset,
                            language=language,
                            value_chars=value_chars
                        )
                    content_type = headers.get(b'Content-Type', b"").decode('utf-8')
                    field_value = FormFile(filename, content_type, disposition_parameters)
                    field_value.file.write(content)
                    field_value.file.seek(0)
                else:
                    # process another field
                    field_value = content.decode('utf-8')
                form.append_value(field_name, field_value)
                # Commented out the print statement to avoid excessive output during benchmarking
                # print(f"块:{part}")

                buffer = buffer[boundary_end:]
                start = 0
        return form


class FormParser:
    def __init__(self, body):
        self.body = body

    async def parse(self):
        pass
