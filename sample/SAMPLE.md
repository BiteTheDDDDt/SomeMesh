# 附录：示例数据

sample文件夹内部提供了传给参赛者程序的数据的实际示例，参赛者可以利用此文件夹内的示例数据来在本地测试自己的程序是否能够正常返回。

示例数据的产生方式为：在一个运行着Istio官方示例应用[Bookinfo](https://istio.io/latest/docs/examples/bookinfo/)的已安装服务网格的Kubernetes集群中，用fortio对Bookinfo应用进行压力测试，并收集容器资源用量和访问日志信息。

示例数据中提供了两组数据：
* podInfo-1.json和accesslog-1.txt：这组数据是在网格内所有Sidecar资源上限都设定为1核、2G的情况下测试得出的。
* podInfo-2.json和accesslog-2.txt：这组数据是在网格内所有Sidecar资源上限都设定为0.1核、128Mi的情况下测试得出的。

## 测试方法

### 前提
* 本机已经安装docker
* 本机已经安装python3
### 步骤

1. 启动自己的容器：

进入项目根目录
```bash
docker build -t test-optimizer .
docker run -p 8000:3001 -d test-optimizer
```

2. 将访问日志提前拷贝至容器中路径

```bash
docker cp sample/accesslog-1.txt {你的容器id}:/app/accesslog.txt
```

3. 利用示例数据生成请求内容，并请求自己的容器

sample中提供了一个非常简单的测试脚本`test.py`，当然参赛者可以利用这些数据选择任意方式进行本地测试

```bash
cd sample
python test.py
```