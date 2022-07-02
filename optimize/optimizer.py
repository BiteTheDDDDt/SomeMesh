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
    '''
    resources = []
    for container in containers:
        cpu_limit -= container['cpu']
        memory_limit -= container['memory']

        if container['container'] != 'istio-proxy':
            continue

        resource = {
            'service': container['service_name'], 'cpu': 0.1, 'memory': 128000000}

        cpu_limit -= resource['cpu']
        memory_limit -= resource['memory']
        resources.append(resource)

    assert(cpu_limit > 0 and memory_limit > 0)
    resources[0]['cpu'] += cpu_limit
    resources[0]['memory'] += memory_limit
    '''
    optimize_result = {
        'resource': [{
            'service': containers[0]['service_name'],  # 需要修改资源分配的Sidecar所属服务
            'cpu': cpu_limit,  # 需要为该服务Sidecar设置的CPU资源上限，单位：核
            'memory': memory_limit  # 需要为该服务Sidecar设置的内存资源上限，单位：Byte
        }],
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
