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


def get_service_map(containers):
    service_map = {}
    for container in containers:
        service_name = container['service_name']
        pod_name = container['pod_name']

        if service_name not in service_map:
            service_map[service_name] = {}
        if pod_name not in service_map[service_name]:
            service_map[service_name][pod_name] = [None, None, None]

        if container['container'] == 'istio-proxy':
            service_map[service_name][pod_name][0] = container
        else:
            service_map[service_name][pod_name][1] = container
    return service_map


def optimize(containers, accesslog_path, cpu_limit, memory_limit):
    cpu_limit_real = cpu_limit
    memory_limit_real = memory_limit

    service_map = get_service_map(containers)

    resources = []

    avg_cpu = {}
    avg_memory = {}
    for service_name in service_map:
        size = len(service_map[service_name])
        service_cpu = 0
        service_memory = 0
        for pod_name in service_map[service_name]:
            proxy = service_map[service_name][pod_name][0]
            service_cpu += proxy['cpu']
            service_memory += proxy['memory']

        avg_cpu[service_name] = 1.0*service_cpu/size
        avg_memory[service_name] = 1.0*service_memory/size

        resource = {
            'service': service_name, 'cpu': lowest_cpu, 'memory': lowest_memory}
        cpu_limit -= size*lowest_cpu
        memory_limit -= size*lowest_memory
        resources.append(resource)

    sum_cpu = sum([avg_cpu[service_name] * len(service_map[service_name])
                  for service_name in avg_cpu])
    sum_memory = sum([avg_memory[service_name] * len(service_map[service_name])
                     for service_name in avg_memory])

    offset = 0
    for service_name in service_map:
        resources[offset]['cpu'] += avg_cpu[service_name]/sum_cpu*cpu_limit-eps
        resources[offset]['memory'] += int(
            avg_memory[service_name]/sum_memory*memory_limit)
        offset += 1

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

    # assert(check_result_valid(resources, service_map,
    #                           cpu_limit_real, memory_limit_real))
    return optimize_result
