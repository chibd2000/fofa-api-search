# fofa
爬取fofa 基于api  

编写原因：去年大二在苏州公司实习的时候写的代码忘记拷走了，现在只能重新大概写下自己用...  

1、gevent模块异步请求  
2、xlsx文档展示  
3、基于api实现   
4、端口服务识别（单纯通过fofa的端口来判断，并不是请求对应的端口看指纹来识别）  
  
配置： 
![image](https://github.com/adezz/fofa/blob/main/pic/config.png)
  
效果：  
![image](https://github.com/adezz/fofa/blob/main/pic/resutl.png)
  
========2021.05.10=========  
1、自己把请求不存在的url也进行了记录  
2、修正了下80 443端口的请求，之前代码写的可能会http://a.com:443 这种情况...  
  
![image](https://github.com/adezz/fofa/blob/main/pic/result_2.png)
