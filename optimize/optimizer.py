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
    print("cpu_limit: ", cpu_limit)
    print("memory_limit: ", memory_limit)

    print("containers size: ", len(containers))
    for container in containers:
        print("container: ", container)
        # 'service_name' Pod所属的服务名称
        # 'ip'           Pod的IP
        # 'pod_name'     Pod的名称
        # 'container'    Pod内容器的名称，名称为istio-proxy的容器就是Sidecar容器
        # 'cpu'          容器在上一轮测试中的平均cpu占用，单位：核
        # 'memory'       容器在上一轮测试中的平均内存占用，单位：Byte

    accesslogs = []
    with open(accesslog_path, 'r', encoding='utf-8') as accesslog_file:
        for line in accesslog_file:
            accesslog = json.loads(line)
            accesslogs.append(accesslog)
            print("accesslog: ", accesslog)
            # 'duration'                  请求时延，e.g. 28
            # 'downstream_remote_address' 发送方Pod IP、端口，e.g. 10.41.0.79:44750
            # 'upstream_host'             接收方Pod IP、端口，e.g. 10.41.0.139:9080
            # 'bytes_sent'                请求大小，e.g. 39
            # 'bytes_received'            响应大小，e.g. 0
            # 'path'                      请求路径，e.g. /reviews

    resources = []
    for container in containers:
        resource = {
            'service': container['service_name'], 'cpu': 0.1, 'memory': 128000000}

        cpu_limit -= resource['cpu']
        memory_limit -= resource['memory']
        resources.append(resource)

    resources[0]['cpu'] += cpu_limit
    resources[0]['memory'] += memory_limit

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

    print("optimize_result: ", optimize_result)
    return optimize_result
