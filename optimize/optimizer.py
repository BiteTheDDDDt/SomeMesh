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


def optimize(containers, accesslog_path, cpu_limit, memory_limit):
    resources = []
    for container in containers:
        if container['container'] != 'istio-proxy':
            continue

        # resource = {
        #    'service': container['service_name'], 'cpu': 0.1, 'memory': 128000000}

        resource = {
            'service': container['service_name'], 'cpu': cpu_limit, 'memory': memory_limit}

        cpu_limit -= resource['cpu']
        memory_limit -= resource['memory']
        resources.append(resource)
        break

    # resources[0]['cpu'] += cpu_limit
    # resources[0]['memory'] += memory_limit

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

    return optimize_result
