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


def get_ip_to_service(containers):
    ip_to_service = {}
    for container in containers:
        ip_to_service[container['ip']] = container['service_name']
    return ip_to_service


def update_request(ip, ip_to_service, request_number_map, request_byte_map, accesslog):
    if ip in ip_to_service:
        service_name = ip_to_service[ip]
        request_number_map[service_name] += 1
        request_byte_map[service_name] += accesslog['bytes_sent'] + \
            accesslog['bytes_received']


def optimize(containers, accesslog_path, cpu_limit, memory_limit):
    cpu_limit_real = cpu_limit
    memory_limit_real = memory_limit

    service_map = get_service_map(containers)
    ip_to_service = get_ip_to_service(containers)
    resource_map = {}

    request_number_map = {}
    request_byte_map = {}
    with open(accesslog_path, 'r', encoding='utf-8') as accesslog_file:
        for line in accesslog_file:
            accesslog = json.loads(line)

            post_ip = accesslog['downstream_remote_address'].split(':')[0]
            update_request(post_ip, ip_to_service,
                           request_number_map, request_byte_map, accesslog)

            get_ip = accesslog['upstream_host'].split(':')[0]
            update_request(get_ip, ip_to_service,
                           request_number_map, request_byte_map, accesslog)

    request_number_sum = sum([request_number_map[service_name]
                             for service_name in request_number_map])
    request_byte_sum = sum([request_byte_map[service_name]
                           for service_name in request_byte_map])

    for service_name in service_map:
        size = len(service_map[service_name])
        resource_map[service_name] = {
            'service': service_name, 'cpu': lowest_cpu, 'memory': lowest_memory}
        cpu_limit -= size*lowest_cpu
        memory_limit -= size*lowest_memory

    for service_name in service_map:
        size = len(service_map[service_name])
        resource_map[service_name]['cpu'] += 1.0*request_number_map[service_name] / \
            request_number_sum*cpu_limit/size-eps
        resource_map[service_name]['memory'] += int(
            request_byte_map[service_name]/request_byte_sum*memory_limit/size)

    resources = [resource_map[service_name] for service_name in resource_map]

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

    # assert(check_result_valid(resources, service_map,  cpu_limit_real, memory_limit_real))
    return optimize_result
