'''
基于TCP服务器的静态Web服务器_返回指定页面数据.py
'''

# 导入模块
import socket
import threading
import sys

# 导入框架应用程序模块

from framework import application


# 实现这个类
class SocketServer(object):
    # 实现初始化方法,在实现这个对象时,就将Socket的准备工作做好
    def __init__(self,port):
        self.__server = socket.socket()
        self.__server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,True)
        self.__server.bind(('',port))
        self.__server.listen(128)


    # 实现一个子线程的任务函数,参数接收客户端对象和信息
    def __handle_task(self,client, ip_port):
        print('客户端 %s 使用 %s 端口连接成功....' % (ip_port[0], ip_port[1]))

        # 接收数据
        recv_data = client.recv(1024).decode()
        # 输出浏览器发过来的请求报文
        print(recv_data)

        # 判断
        if len(recv_data) == 0:
            print('客户端 %s 下线了....' % ip_port[0])
            client.close()

        else:

            # 分割请求报文,获取到请求资源路径,以备后面打开文件使用
            request_data = recv_data.split()

            # 获取请求资源路径
            request_path = request_data[1]
            # 因为请求资源可以会有参数,那么如果有参数就继续分割
            # /?name = user & passwd = 123
            if request_path.find('?') != -1:
                # 满足条件说明有参数,继续分割
                params = request_path.split('?')
                request_path = params[0]

            # 继续判断,如果请求的资源路径是 / 那么默认让服务器返回 首页
            if request_path == '/':
                request_path = '/index.html'
            print('请求的路径是: %s' % request_path)


            # 添加代码, 用来判断区别请求的资源是静态还是动态
            if request_path.endswith('.html'):
                # 动态资源

                # 定义一个字典,用来存所有的请求中的参数数据,传给框架应用程序使用
                env = {
                    # 使用 PATH_INFO 来保存请求的资源地址
                    'PATH_INFO': request_path
                }
                response_body = application(env, self.start_response)

                # 准备拼接响应报文
                response_line = 'HTTP/1.1 %s\r\n' % self.__status
                response_head = 'Server: MiniWebServer v1.0\r\n'
                for t in self.__prarms:
                    response_head += '%s: %s\r\n' % (t[0],t[1])
                response_data = (response_line + response_head + '\r\n' + response_body).encode()
                client.send(response_data)
                client.close()

            else:
                # 静态资源

                try:
                    # 先读取文件
                    with open('static' + request_path, 'rb') as file:
                        content = file.read()
                except Exception as e:
                    # 有异常,可能访问的资源文件不存在

                    response_line = 'HTTP/1.1 404 Not Found\r\n'
                    response_head = 'Server: PWS/1.0\r\n'
                    response_body = '<h1>Page Not Found !!!!</h1>'
                    response_data = (response_line + response_head + '\r\n' + response_body).encode()
                    client.send(response_data)

                else:
                    # 正常打开文件,没有异常
                    # 拼接响应报文,返回一个固定数据
                    # 定义响应行
                    response_line = 'HTTP/1.1 200 OK\r\n'

                    # 定义一个响应头
                    response_head = 'Server: PWS/1.0\r\n'

                    # 定义一个响应体
                    response_body = content

                    # 拼接响应报文
                    response_data = (response_line + response_head + '\r\n').encode() + response_body

                    # 向客户端回传响应报文数据
                    client.send(response_data)
                finally:
                    # 关闭连接
                    client.close()


    # 启动方法
    def start(self):
        # 输出提示信息
        print('Serving ON 127.0.0.1:8000 .......')

        # 让服务器死循环接收客户端的请求
        while True:
            # 接收请求
            client, ip_port = self.__server.accept()

            # 实现一个子线程对象,让他去一边去处理客户端的接收数据请求
            t = threading.Thread(target=self.__handle_task, args=(client,ip_port),daemon=True)
            t.start()

        # self.__server.close()



    # 定义一个用来进行回调的函数,做为参数传给框架程序
    def start_response(self,status, prarms):
        # 该方法接收两个参数,参数一是应用程序返回来的状态码,参数二是返回来的数据的相关格式信息
        # 只把返回的数据记录下来
        self.__status = status
        self.__prarms = prarms

# 入口
if __name__ == '__main__':

    # 通过判断来找出来命令行传入的端口
    print('请以以下方式启动服务器: python3 xxx.py 8000')

    # 判断
    if len(sys.argv) != 2:
        print('启动参数有误,请重新启动...')
    else:
        port = sys.argv[1]

        if port.isdigit():
            port = int(port)

            # 创建一个多任务的socket服务器对象
            server = SocketServer(port)
            # 并且启动
            server.start()
        else:
            print('端口不是数字')

