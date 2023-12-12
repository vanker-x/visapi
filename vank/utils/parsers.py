import typing as t
from urllib.parse import parse_qsl, unquote
from vank.utils.datastructures import Form, SpooledUploadFile


class ParseException(Exception):
    """
    解析时异常
    """


class MultiPartFormParser:
    """
    This is multipart-form/data parser
    Grammar:
            content-disposition  = "Content-Disposition" ":" disposition-type *( ";" disposition-parm )

             disposition-type    = "inline" | "attachment" | disp-ext-type ; case-insensitive

             disp-ext-type       = token

             disposition-parm    = filename-parm | disp-ext-parm

             filename-parm       = "filename" "=" value | "filename*" "=" ext-value

             disp-ext-parm       = token "=" value | ext-token "=" ext-value

             ext-token           = <the characters in token, followed by "*">
    based on https://datatracker.ietf.org/doc/html/rfc6266#section-4.1
    """

    def __init__(self, boundary: t.Union[str, bytes], body: bytes):
        """
        initialize parser
        :param boundary: the sep of each parts
        :param body: bytes body
        """
        self.body = body
        self.boundary = boundary

    def run(self):
        """
        start process
        :return:
        """
        form = Form()
        parts = self.body.split(b"--" + self.boundary)
        parts = parts[1:-1]
        for part in parts:
            # Split the header and content of this part,it looks like b'\r\n<header>\r\n\r\n<content>\r\n'
            header, content = part.split(b'\r\n\r\n', 1)
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
            # try to get charset from disposition-parameters or utf-8
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
                field_value = SpooledUploadFile(filename, content_type, disposition_parameters)
                field_value.write(content)
                field_value.seek(0)
            else:
                # process other field
                field_value = content.decode('utf-8')
            form.append_value(field_name, field_value, error=False)
        return form


class FormParser:
    """
    This is application/x-www-form-urlencoded form parser
    """

    def __init__(self, body: bytes):
        self.body = body

    def run(self):
        form = Form()
        for key, value in parse_qsl(self.body.decode("latin1"), keep_blank_values=False):
            form.append_value(key, value, error=False)
        return form
