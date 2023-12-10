# lazytool
学习通多种方式签到；雨课堂自动答题；...
## 学习通
学习通图片签到，位置签到，扫码签到。
配置信息需要自己填写，phone和password是必须填写的，有这个才能登录学习通。剩下的是位置签到的参数
扫码签到需要让好兄弟拍一下二维码，二维码里面有enc参数，在mode_info加一下，mode参数为qrcode。
图片签到，mode_info的mode为pic,同时需要将图片路径加入mode_info的filepath参数中。
位置签到需要在config配置一下longitude和latitude，这个是经纬度，address为地址，会显示在什么地方打卡
## 雨课堂
直接调用ykt_user,传参的name可以随便，初次登录会获取一张登录二维码,手动微信扫描登录，会将cookie保存，应该有效期是两周左右。
多线程好像会出现一些问题，可以自己调一调。它的主要功能就是你可以写一个定时任务，比如上课时间是八点，定时八点调用ykt_user函数，就会监听此时是否有课程正在上课，有的话会自动签到进入课堂，并且通过socket实时监听服务端数据，雨课堂的程序员可能比较偷懒，在每次创建一个presentation，就是开始播放幻灯片的时候会在socket返回一个id，这个id就可以获取这次播放的所有的幻灯片，包括习题页，更离谱的是习题页幻灯片的答案也在享用的内容中......
为了可以实时进行查看答题情况和一些状态信息，采用了企业微信机器人的微信插件（推送到微信里），这个具体怎么操作会简单，只需要创建一个企业，有官方文档可以查阅。这个可以在yuketang类的初始化方法中修改debug和wx两个参数。debug为true就是开启输出，wx为true就是开启企业微信消息推送。因为会导入qywxbot的send.py，也可以直接把send.py跟雨课堂放在一个目录下，修改一下import 信息就可以


## 其他
这个项目只是为了偷懒不想上早八写的，还有很多bug和可以优化的地方，很多地方写的很烂。

## 声明
如果有任何侵权或者违规行为，请联系我删除。

