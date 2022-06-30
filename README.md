# 针对Sidecar模式下的服务网格数据面应用服务访问QPS和延时的优化 —— 提交示例代码
2022年天池-云原生编程挑战赛，服务网格赛道提交示例代码
## 提交方式
1. 报名参加“2022年云原生编程挑战赛 —— 赛道一：针对 Sidecar 模式下的服务网格数据面应用服务访问 QPS 和延时的优化”
2. 在code.aliyun.com注册一个账号，新建一个仓库，将大赛官方账号添加为项目成员，权限为Reporter。 **大赛官方账号为`cloudnative-contest`**
3. fork或者拷贝本仓库代码至自己的仓库，修改`optimize/optimizer.py`中提供的`ready`和`optimize`函数，实现自己的逻辑。（请不要修改`server.py`，会造成评测失败）
4. 在天池提交成绩的入口，提交自己的仓库git地址，等待评测结果。
## 赛题说明
容器作为云原生应用的交付物，既解决了环境一致性的问题，又可以更细粒度的限制应用资源，但是随着微服务和 DevOps 的流行，容器作为微服务的载体得以广泛应用。Kubernetes 作为一种容器编排调度工具，解决了分布式应用程序的部署和调度问题。

在服务网格技术出现之前，可以使用 SpringCloud、Netflix OSS 等，通过在应用程序中集成 SDK，编程的方式来管理应用程序中的流量。但是这通常会有编程语言限制，而且在 SDK 升级的时候，需要修改代码并重新上线应用，会增大人力负担。服务网格技术使得流量管理变得对应用程序透明，使这部分功能从应用程序中转移到了平台层，成为了云原生基础设施。以 Istio 为首的服务网格技术，正在被越来越多的企业所瞩目。Istio 使用 Sidecar 借助 iptables 技术实现流量拦截，可以处理所有应用的出入口流量，以实现流量治理、观测、加密等能力。要了解更多有关服务网格Istio的基础知识，可以参考[istio官方网站](https://istio.io/latest/zh/)。

实践过程中我们发现，引入Istio服务网格技术带来的缺点之一是性能损失。 在典型情况下，引入服务网格技术之后会导致 QPS（每秒查询数）下降 ，以及请求延迟增加 。其中的原因可以大致分为以下几个方面（包括但不限于）：

1） Istio 设计之初的目标就是通过协议转发的方式服务于服务间流量，让服务网格尽可能对应用程序透明，从而使用了 IPtables 劫持流量。实践过程中我们发现，因为 IPtables conntrack 模块所固有的问题，随着网格规模的扩大，Istio 的性能问题开始显现。使用 iptables 的技术带来的对出入口请求的拦截，造成大量的性能损失，这对一些性能要求高的场景有明显的影响。

2）Istio控制平面默认会监听和处理Kubernetes集群中所有命名空间中的所有资源,  这对于一定规模的集群来说, 在服务发现、配置推送等方面都存在一定的性能影响。

3）随着对服务之前的数据传输、数据真实性、完整性和隐私性越来越重视,  零信任安全变得更加重要。要实现零信任，可以使用mTLS 为您的服务发出的每个请求提供加密。然而, 使用 mTLS 实现的加密隧道增加了微服务到微服务的延迟时间。

除了性能损失的方面，在服务网格数据面侧，每个服务Pod都会注入一个Sidecar代理、而每个Sidecar代理都是一个独立的容器，这导致当集群中服务规模持续增长时，服务网格的Sidecar代理将消耗不可忽视的集群资源。

目前在软件、硬件层面，从多种角度都提出了一些方案来提升服务网格的整体性能，同时尽可能的降低数据面侧Sidecar代理所消耗的资源。在软件层面，可以优化数据面的Sidecar配置、对服务网格的控制面服务发现的效率提升；此外，也可以考虑引入eBPF替代iptables, 或者通过启用eBPF代替部分Envoy代理的能力等。在硬件层面，可以在Sidecar代理通信过程中加入基于新指令集的扩展功能, 例如，阿里云服务网格ASM就可以在搭载Intel Ice Lake平台的集群节点上，基于Multi-Buffer 多缓冲区处理结合AVX512指令对一些常见加密算法的性能提升，从而提升Sidecar代理的TLS通信效率。

本赛题希望从Sidecar代理资源分配、Sidecar配置调优、硬件优化几个角度出发，通过构建一种服务网格性能与资源占用动态优化系统，实现在尽量减少Sidecar代理资源消耗的情况下、也尽可能降低集群中服务的请求时延。这涉及以下几个方面的优化：

1. 合理分配Sidecar的资源：出于处理与转发请求的需要，每个Sidecar代理都需要一定量的资源，被分配的资源越多，处理和转发请求的过程越快、集群中服务的请求时延也会降低；但同时，也不能无限制地为每个Sidecar代理分配资源，因为这会迅速耗尽集群中的有限资源，后续集群中服务的扩容以及部署新的服务也会失败。
1. 平台特性调优：本赛题的评测环境搭建于阿里云服务网格ASM平台，平台的集群节点为基于Intel Ice Lake的ECS节点，支持Multi-buffer多缓冲区处理和AVX512指令集，鼓励参赛者使用这一平台特性进行调优。
1. Sidecar配置调优：可以通过服务网格Istio的Sidecar与EnvoyFilter 自定义资源来针对性地调整Sidecar代理的配置内容，鼓励参赛者尝试使用Sidecar与EnvoyFilter自定义资源进行网格调优。
### 问题描述
我们可以将构建上述动态优化系统的需求总结为以下问题：
#### 已知
整体评测环境是一个基于Kubernetes集群和服务网格平台的微服务架构应用，对外暴露多个http接口，满足以下条件：<br />1、所有外部请求都经过一个入口网关发送给Kubernetes集群中的服务。<br />2、Kubernetes集群中的服务存在复杂的依赖关系，每条入口网关发送的请求最终都对应一条调用链路，链路上的每个服务都接受来自下游服务的请求、 并向上游服务发送请求。<br />3、Kubernetes中的每个服务都有若干端点，被称为Pod，发送往服务的请求由具体的Pod进行响应，请求将被随机发往服务对应的其中一个Pod。<br />4、一个Pod中存在两个容器，除提供服务的业务容器外，还有一名为istio-proxy的Sidecar容器。这是因为服务网格会为每个Pod都注入一个Sidecar代理容器，所有流经Pod的流量都由对应Sidecar代理进行拦截和转发。<br />

#### 赛题要求
参赛者需要实现一个服务网格性能与资源占用动态优化系统（下称“系统”），具体来说：

##### 系统输入
服务网格会以一个固定的时间间隔，分若干轮向系统上报网格信息，这包括当前服务网格中服务Pod的信息、以及该时段内服务之间发送请求的访问日志（请求都为http请求）：

- Pod信息：服务网格会向系统上报当前集群内所有Pod的名称、ip地址、Pod中业务容器占用cpu、内存资源量、以及Pod中Sidecar代理容器cpu、内存占用资源量
- 访问日志：服务网格会向系统发送在当前时段内服务之间调用发送请求的日志信息，每条日志对应一条请求，包括以下信息：请求源头服务名、请求目标服务名、请求源头Pod ip、请求目标Pod ip、请求字节数大小、该条请求的时延
- CPU资源限制：规定当前时间集群对所有Sidecar容器的总CPU资源限制，不允许给Sidecar容器分配总额超出该限制的CPU资源
- 内存资源限制：规定当前时间集群对所有Sidecar容器的总内存资源限制，不允许给Sidecar容器分配总额超出该限制的内存资源

##### 系统输出
每轮接受服务网格输入后，系统都可以返回不同维度的优化配置，评测程序会帮助将系统返回的优化配置应用在服务网格平台中，以达到优化的目标。优化的目标是使得在Sidecar代理容器资源占用尽可能小的情况下，网关发送的请求的时延尽可能低。<br />优化配置包括以下部分：<br />1、分配资源值：系统可以为每个服务的Sidecar容器指定需要分配多少的CPU和内存资源。<br />**注意**：为Sidecar分配的CPU资源不得小于0.1核、内存资源不得小于128Mi。否则将记为0分。<br />2、平台特性：系统可以设定基于测评平台的multi-buffer特性的开启或关闭、以及multi-buffer特性的pollDelay参数，以达成通信性能优化的作用。使用multi-buffer可以明显提高服务网格的性能，参赛者必须使用multi-buffer特性来优化网格通信性能，有关multi-buffer，可以参考：<br />[https://help.aliyun.com/document_detail/349282.html](https://help.aliyun.com/document_detail/349282.html)<br />3、服务网格自定义资源：系统可以返回EnvoyFilter和Sidecar两种Istio服务网格平台中的自定义资源，评测程序会将这些自定义资源应用到网格平台上。鼓励参赛者尝试使用服务网格的自定义资源优化网格配置。有关这两种自定义资源，可以参考：[https://istio.io/latest/zh/docs/reference/config/networking/sidecar/](https://istio.io/latest/zh/docs/reference/config/networking/sidecar/)<br />[https://istio.io/latest/zh/docs/reference/config/networking/envoy-filter/](https://istio.io/latest/zh/docs/reference/config/networking/envoy-filter/)

## 代码说明

### 系统输入输出说明
评分程序以http接口的形式与参赛者的应用进行对接，参赛者需要开发一个应用，提供以下http接口：

1. GET /ready：评分程序会探测此接口，当返回200状态码时即判断选手程序就绪，并进行后续操作
2. POST /optimize：评分程序在评分过程中会定期调用此接口，代表不同时段服务网格为系统上报的信息。在POST body中以json格式为选手应用提供Pod信息与访问日志。选手应用需要同样返回一个固定格式的json，用来代表参赛者应用本轮作出的决策。即：每轮评分程序都会调用/optimize接口、传入上一轮运行中产生的资源使用、访问日志这些可观测数据，并根据接口的返回设置服务网格Sidecar参数，重新运行压力测试，并将可观测数据传给下一轮的调用。第一轮时，评测程序将会首先以所有Sidecar 0.1核、128Mi的默认资源限制运行一次压力测试，再传给/optimize接口。

POST request body为json格式，提供两个json数组，其中pods是当前集群内的Pod信息，accesslogs是本时段内产生的访问日志，此外还提供当前集群资源上限，如：
```json
{
  "containers":[
    {"service_name": "productpage", "pod_name": "productpage-12345", "container": "productpage", "ip":"10.12.123.33", "app": 1, "sidecar": 0.1}, 
    {"service_name": "reviews", "pod_name": "reviews-67890", "container": "istio-proxy",  "ip":"10.12.123.34", "app": 1, "sidecar": 0.1}
   ], 
  "accesslog_path": "/path/to/accesslog",
  "cpu_limit": 12,
  "memory_limit": 1000000000,
}
```
（1）containers数组记录了每个容器的实际资源消耗。对于containers数组中的每项pod信息，它们都包含以下字段：

- service_name：string，pod对应的服务名称
- pod_name：string，pod的名称
- ip：string，pod的ip地址
- container：string，pod中的容器名称（Sidecar的名称都为istio-proxy，其它名称为业务容器）
- cpu：number，该容器所占CPU资源大小，单位核
- memory：number，该容器所占内存资源大小，单位Byte（如128000000就代表128Mi）

**注**：所有服务都位于default命名空间下

（2）accesslog_path是一个日志文件路径，系统可以读取这些访问日志记录，每一行是一条访问日志，为json字符串格式。<br />对于具体的每项访问日志，它们都包含以下字段：

- downstream_remote_address：string，具体发送请求的Pod ip和端口
- upstream_host：string，具体接受请求的Pod ip和端口
- duration：number，该条请求的延时
- bytes_sent：number，发送的请求大小
- bytes_received：number，接收的响应大小
- path：string，请求发送的路径

除上述字段外，访问日志中还包括请求返回码、协议等字段，同样可以利用。有关访问日志的字段格式的全部信息，可以参考：[https://help.aliyun.com/document_detail/322801.html#info-2zp-n24-1fa](https://help.aliyun.com/document_detail/322801.html#info-2zp-n24-1fa)；有关访问日志中每个字段的意义，可以参考：[https://www.envoyproxy.io/docs/envoy/latest/configuration/observability/access_log/usage](https://www.envoyproxy.io/docs/envoy/latest/configuration/observability/access_log/usage)。

**注**：评分程序仅提供Sidecar outbound访问日志（仅记录请求发送方的日志，没有请求接收方的日志）
<br />（3）cpu_limit记录了当前集群允许分配给Sidecar容器的CPU资源总量，单位：核<br />（4）memory_limit记录了当前集群允许分配给Sidear容器的内存资源总量，单位：Byte<br />选手应用的接口在接受上述数据后，应返回类似以下格式的json对象，表示优化决策：
```json
{
  "resource": [{"service":"productpage", "cpu": 0.2, "memory": 2455666}]
  "istio_cr": []
  "features": {
    "multi_buffer": {
       "enabled": true,
       "poll_delay": "0.2s"
    }
  }
}
```
返回的json对象中包含以下字段：<br />1、resource<br />resource是一个json数组，数组中的每一项都包含以下字段，以代表系统决策最多分配给该Pod的Sidecar代理多少资源：

- service：string，**服务**的名称，代表要为哪个服务的Sidecar设定资源值，注意：只能同时为一个服务的所有Sidecar设定统一的资源值
- cpu：number，系统决定为该Pod中的Sidecar代理容器最多分配的CPU资源值，单位：核
- memory：number，系统决定为该Pod中的Sidecar代理容器最多分配的内存资源值，单位：Byte

如果不为某服务的Sidecar设定资源值，则该服务的Sidecar所用资源会被默认限制在最低的0.1核、128Mi内存。<br />2、istio_cr<br />istio_cr是一个字符串格式的数组，用户如果希望应用Sidecar或者EnvoyFilter自定义资源，可以将这些自定义资源的YAML格式字符串附加在这个数组中，评测程序会帮助应用至评测用的服务网格平台。<br />3、features<br />可以在此字段中设置服务网格的平台特性，具体来说，可以设置以下字段：

- multi_buffer：可以设置服务网格基于Intel Ice Lake平台的multi-buffer特性，可设置如下两个属性
   - enabled：bool，是否启用multi-buffer特性
   - poll_delay：string，设定multi-buffer特性的策略拉取延迟 （如 0.2s），必须是以"s"结尾的表示秒的时间单位

## 代码结构说明
示例代码以Python实现，基于Python3 + Flask，主要有以下几个组成部分：
* server.py：代码的服务器部分，规定了监听的端口/API接口。**请不要修改此文件，以免导致代码提交后测评失败**
* requirementes.txt：Python依赖项，允许自定义代码依赖项。
* Dockerfile：用于在测试提交代码时构建docker容器，**无法被修改，即使修改在构建时也会被覆盖回去**
* optimize/optimize.py：server将调用optimize包内的optimize()和ready()两个方法、对应实现/optimize和/ready两个API。需要修改optimize包的内容来实现自定义的网格优化逻辑。由于测试分为多伦进行，可以在代码中维护每轮测试的数据和状态。

**注意**：
<br />1、在为Sidecar（istio-proxy容器）分配资源时要考虑资源限制。若某轮测试时发现参赛者为Sidecar容器分配的CPU/内存资源总量超过了该轮的资源总量限制，则分数会记为0。<br />2、同理，为每个Sidecar（istio-proxy容器）分配的CPU资源不得小于0.1核、内存资源不得小于128Mi（128000000）。否则分数将记为0分。<br/>3、不允许在代码中hack测试环境中使用的具体服务配置或请求内容