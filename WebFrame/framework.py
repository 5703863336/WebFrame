'''

实现读取个人中心页面展示并实现简单路由

'''
from pymysql import Connect


# application()函数就是符合WSGI标准的一个HTTP处理函数，它接收两个参数：
# environ：一个包含所有HTTP请求信息的dict对象；
# start_response：一个发送HTTP响应的函数。
# 这个函数返回的数据就是客户端请求的数据


# 定义一个空字典做为路由表

router_table = {}

# 再定义一个可以接收参数的装饰器来自动维护路由表
def router(url):
    def outer(func):
        def inner(*args, **kwargs):
            content = func(*args, **kwargs)
            return content
        # 将内函数通过传入的地址存到路由表中
        router_table[url] = inner
        return inner
    return outer





def application(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/html;charset=utf8')])

    # 先通过参数将服务器转发过来的请求地址取出来
    request_url = environ['PATH_INFO']
    print('*'*100)
    print(router_table)
    print('*' * 100)

    # 判断
    func = other
    if request_url in router_table:
        func = router_table[request_url]

    content = func()
    return content


# 封装首页函数的代码
@router('/index.html')
def index():
    # 读取模板文件
    with open('templates/index.html','r',encoding='utf8') as file:
        content = file.read()


    # 下面的开发思想使用的是 前后端不分离思想

    # 首页固定数据
    # 先将 标签中的固定数据变成占位符
    row_str = """ 
    	<tr>
        	<td>%s</td>
        	<td>%s</td>
      	  	<td>%s</td>
        	<td>%s</td>
        	<td>%s</td>
        	<td>%s</td>
        	<td>%s</td>
        	<td>%s</td>
        	<td>
            	<input type="button" value="添加" id="toAdd" name="toAdd" systemidvaule="%s">
        	</td>
    	</tr>  
    """

    # 连接数据库
    db_connect = Connect(host='localhost',port=3306,user='root',password='123123',database='stock_db',charset='utf8')
    cur = db_connect.cursor()
    sql_str = ''' select * from info '''
    cur.execute(sql_str)
    result = cur.fetchall()
    cur.close()
    db_connect.close()

    # 遍历结果,并将结果添加到格式字符串中
    all_data = ''
    for t in result:
        all_data += row_str % (t[0],t[1],t[2],t[3],t[4],t[5],t[6],t[7],t[1])

    # 字符串是一个不可变对象,所以要接收一下替换后的数据并返回
    content = content.replace('{%content%}',all_data)

    # 将模板文件中的内容返回
    return content


# 封装个人中心页面,读取模块并展示
@router('/center.html')
def center():
    # 读取模板,并返回
    with open('templates/center.html', 'r') as file:
        content = file.read()

    return content

# 其它页面
def other():
    return '<h1>暂无数据</h1>'


# 定义一个新闻页面
# @router('/news.html')
def news():
    return '<h1>新闻页面</h1>'