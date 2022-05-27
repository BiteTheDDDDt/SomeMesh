# edit this file
# 编辑此文件!
import json

# 一个可以应用于Istio服务网格平台的Sidecar资源示例
# 有关Sidecar和EnvoyFilter资源，可参考：
# https://istio.io/latest/zh/docs/reference/config/networking/sidecar/
# https://istio.io/latest/zh/docs/reference/config/networking/envoy-filter/
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
    return 'ready'

# 修改此方法实现自己的网格资源优化逻辑
def optimize(containers, accesslog_path, cpu_limit, memory_limit):
    accesslogs = []
    # 读取访问日志文件
    with open(accesslog_path, 'r', encoding='utf-8') as accesslog_file:
        for line in accesslog_file:
            accesslog = json.loads(line)
            print(accesslog['duration']) # 请求时延，e.g. 28
            print(accesslog['downstream_remote_address']) # 发送方Pod IP、端口，e.g. 10.41.0.79:44750
            print(accesslog['upstream_host']) # 接收方Pod IP、端口，e.g. 10.41.0.139:9080
            print(accesslog['bytes_sent']) # 请求大小，e.g. 39
            print(accesslog['bytes_received']) # 响应大小，e.g. 0
            print(accesslog['path']) # 请求路径，e.g. /reviews
            accesslogs.append(accesslog)
    for container in containers:
        print(container['service_name']) # Pod所属的服务名称
        print(container['ip']) # Pod的IP
        print(container['pod_name']) # Pod的名称
        print(container['container']) # Pod内容器的名称，名称为istio-proxy的容器就是Sidecar容器
        print(container['cpu']) # 容器在上一轮测试中的平均cpu占用，单位：核
        print(container['memory']) # 容器在上一轮测试中的平均内存占用，单位：Byte
    
    optimize_result = {
        'resource': [ # 通过resource字段为Sidecar容器分配资源，分配的总资源量分别不得超过CPU和内存资源上限
            {
                'service': containers[0]['service_name'], # 需要修改资源分配的Sidecar所属服务
                'cpu': 0.1, # 需要为该服务Sidecar设置的CPU资源上限，单位：核
                'memory': 512000000# 需要为该服务Sidecar设置的内存资源上限，单位：Byte
            }
        ],
        'istio_cr': [sidecar_example], # 通过istio_cr字段向服务网格应用Sidecar或EnvoyFilter资源来进行优化
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