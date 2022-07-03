import json

sidecar_example = '''
apiVersion: networking.istio.io/v1alpha3
kind: Sidecar
metadata:
  name: default
spec:
  egress:
  - hosts:
    - "./*"
    - "istio-system/*"
'''


def ready():
    return 200


def check_result_valid(resources, service_map, cpu_limit, memory_limit):
    for resource in resources:
        size = len(service_map[resource['service']])
        cpu_limit -= size*resource['cpu']
        memory_limit -= size*resource['memory']
    assert(cpu_limit >= 0 and memory_limit >= 0)


def optimize(containers, accesslog_path, cpu_limit, memory_limit):
    cpu_limit_real = cpu_limit
    memory_limit_real = memory_limit

    service_map = {}
    for container in containers:
        service_name = container['service_name']
        pod_name = container['pod_name']

        if service_name not in service_map:
            service_map[service_name] = {}
        if pod_name not in service_map[service_name]:
            service_map[service_name][pod_name] = [0, 0]

        if container['container'] == 'istio-proxy':
            service_map[service_name][pod_name][0] = container
        else:
            service_map[service_name][pod_name][1] = container

    resources = []
    for service_name in service_map:
        size = len(service_map[service_name])

        resource = {
            'service': service_name, 'cpu': 0.1, 'memory': 128000000}

        cpu_limit -= size*resource['cpu']
        memory_limit -= size*resource['memory']
        resources.append(resource)

    size = len(service_map[resources[0]['service']])
    resources[0]['cpu'] += cpu_limit/size
    resources[0]['memory'] += memory_limit/size

    optimize_result = {
        'resource': resources,
        # 通过istio_cr字段向服务网格应用Sidecar或EnvoyFilter资源来进行优化
        'istio_cr': [sidecar_example],
        'features': {
            # 设置使用intel multi-buffer技术加快网格tls通信
            # 参考：https://help.aliyun.com/document_detail/349282.html
            'multi_buffer': {
                'enabled': True,
                'poll_delay': '0.2s'
            }
        }
    }

    check_result_valid(resources, service_map,
                       cpu_limit_real, memory_limit_real)
    return optimize_result
