from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
from fastapi.routing import APIRoute
from time import time

# Define metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['method', 'endpoint']
)

def get_metrics_route():
    async def metrics_route():
        return Response(
            content=generate_latest(),
            media_type=CONTENT_TYPE_LATEST
        )
    return metrics_route

class PrometheusMiddleware:
    def __init__(self, app):
        self.app = app
        
    async def __call__(self, scope, receive, send):
        if scope['type'] == 'http':
            method = scope['method']
            path = scope['path'].split('/')[1]  # Get first path segment
            
            start_time = time()
            
            async def send_wrapper(response):
                if response['type'] == 'http.response.start':
                    status_code = str(response['status'])
                    REQUEST_COUNT.labels(method=method, endpoint=path, status_code=status_code).inc()
                    REQUEST_LATENCY.labels(method=method, endpoint=path).observe(time() - start_time)
                await send(response)
            
            await self.app(scope, receive, send_wrapper)
        else:
            await self.app(scope, receive, send)