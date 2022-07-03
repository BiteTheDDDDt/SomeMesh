import optimizer

containers = [
    {"service_name": "productpage", "pod_name": "productpage-1",
        "container": "productpage"},
    {"service_name": "productpage", "pod_name": "productpage-1",
        "container": "istio-proxy"},
    {"service_name": "productpage", "pod_name": "productpage-2",
     "container": "productpage"},
    {"service_name": "productpage", "pod_name": "productpage-2",
        "container": "istio-proxy"},
    {"service_name": "test", "pod_name": "test-1",
     "container": "test"},
    {"service_name": "test", "pod_name": "test-1",
        "container": "istio-proxy"}
]
accesslog_path = ''
cpu_limit = 10
memory_limit = 1000000000

print(optimizer.optimize(containers, accesslog_path, cpu_limit, memory_limit))
