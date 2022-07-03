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

eps = 1e-12
lowest_cpu = 0.1
lowest_memory = 128000000


def ready():
    return 200


def check_result_valid(resources, service_map, cpu_limit, memory_limit):
    try:
        assert(len(resources) != 0)
    except:
        print("len(resources) != 0", len(resources))
        return False

    for resource in resources:
        size = len(service_map[resource['service']])
        cpu_limit -= size*resource['cpu']
        memory_limit -= size*resource['memory']

        try:
            assert(resource['cpu'] >=
                   lowest_cpu and resource['memory'] >= lowest_memory)
        except:
            print("resource['cpu']>=lowest_cpu and resource['memory']>=lowest_memory",
                  resource['cpu'], resource['memory'])
            return False

    try:
        assert(cpu_limit >= 0 and memory_limit >= 0)
    except:
        print("cpu_limit >= 0 and memory_limit >= 0", cpu_limit, memory_limit)
        return False

    return True


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
            service_map[service_name][pod_name] = [None, None]

        if container['container'] == 'istio-proxy':
            service_map[service_name][pod_name][0] = container
        else:
            service_map[service_name][pod_name][1] = container

    resources = []
    for service_name in service_map:
        size = len(service_map[service_name])

        resource = {
            'service': service_name, 'cpu': lowest_cpu, 'memory': lowest_memory}

        cpu_limit -= size*resource['cpu']
        memory_limit -= size*resource['memory']
        resources.append(resource)

    size = len(service_map[resources[0]['service']])
    resources[0]['cpu'] += cpu_limit/size-eps
    resources[0]['memory'] += int(memory_limit/size-eps)

    optimize_result = {
        'resource': resources,
        'istio_cr': [sidecar_example],
        'features': {
            'multi_buffer': {
                'enabled': True,
                'poll_delay': '0.2s'
            }
        }
    }

    assert(check_result_valid(resources, service_map,
                              cpu_limit_real, memory_limit_real))
    return optimize_result
