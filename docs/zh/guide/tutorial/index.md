```mermaid
graph LR
    0[开始] -->|HTTP请求| A[WebServer]
    A -->|HTTP响应| 0
    A -->|proxy_pass| B[WSGI or ASGI or RSGI]
    B --> A
    B -->|call| C[Python Application]
    C -->|response| B
```