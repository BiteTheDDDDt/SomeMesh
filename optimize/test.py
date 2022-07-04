import optimizer

containers = [
    {"service_name": "productpage", "pod_name": "productpage-1",
        "container": "productpage", "cpu": 0.1, "memory": 128000000},
    {"service_name": "productpage", "pod_name": "productpage-1",
        "container": "istio-proxy", "cpu": 0.1, "memory": 128000000},
    {"service_name": "productpage", "pod_name": "productpage-2",
     "container": "productpage", "cpu": 0.1, "memory": 128000000},
    {"service_name": "productpage", "pod_name": "productpage-2",
        "container": "istio-proxy", "cpu": 0.1, "memory": 128000000},
    {"service_name": "test", "pod_name": "test-1",
     "container": "test", "cpu": 0.1, "memory": 128000000},
    {"service_name": "test", "pod_name": "test-1",
        "container": "istio-proxy", "cpu": 0.1, "memory": 128000000}
]
accesslog_path = ''
cpu_limit = 10
memory_limit = 1000000000

print(optimizer.optimize(containers, accesslog_path, cpu_limit, memory_limit))
