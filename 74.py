import sys
import os
import datetime
import cv2
import threading
import numpy as np
from snap7 import util
from uuid import uuid4
import snap7
from snap7.util import *
import time
import serial
from PyQt5.QtWidgets import QWidget, QApplication,QMainWindow
from camera825 import Ui_MainWindow
from PyQt5.QtCore import QEvent,Qt
from PyQt5 import QtCore,QtGui,QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal
import flask, json
import multiprocessing as mp
import queue
import socket
import os
import imutils
import platform
import time
import tkinter
from tkinter import *
import ctypes
import sys
class NET_DVR_DEVICEINFO_V30(ctypes.Structure):
    _fields_ = [
        ("sSerialNumber", ctypes.c_byte * 48),  # 序列号
        ("byAlarmInPortNum", ctypes.c_byte),  # 模拟报警输入个数
        ("byAlarmOutPortNum", ctypes.c_byte),  # 模拟报警输出个数
        ("byDiskNum", ctypes.c_byte),  # 硬盘个数
        ("byDVRType", ctypes.c_byte),  # 设备类型
        ("byChanNum", ctypes.c_byte),  # 设备模拟通道个数，数字（IP）通道最大个数为byIPChanNum + byHighDChanNum*256
        ("byStartChan", ctypes.c_byte),  # 模拟通道的起始通道号，从1开始。数字通道的起始通道号见下面参数byStartDChan
        ("byAudioChanNum", ctypes.c_byte),  # 设备语音对讲通道数
        ("byIPChanNum",ctypes.c_byte),  # 设备最大数字通道个数，低8位，高8位见byHighDChanNum
        ("byZeroChanNum",ctypes.c_byte),  # 零通道编码个数
        ("byMainProto",ctypes.c_byte),  # 主码流传输协议类型：0- private，1- rtsp，2- 同时支持私有协议和rtsp协议取流（默认采用私有协议取流）
        ("bySubProto",ctypes.c_byte),  # 子码流传输协议类型：0- private，1- rtsp，2- 同时支持私有协议和rtsp协议取流（默认采用私有协议取流）
        ("bySupport",ctypes.c_byte),  # 能力，位与结果为0表示不支持，1表示支持
        ("bySupport1",ctypes.c_byte),  # 能力集扩充，位与结果为0表示不支持，1表示支持
        ("bySupport2",ctypes.c_byte),  # 能力集扩充，位与结果为0表示不支持，1表示支持
        ("wDevType", ctypes.c_uint16),  # 设备型号，详见下文列表
        ("bySupport3",ctypes.c_byte),  # 能力集扩展，位与结果：0- 不支持，1- 支持
        ("byMultiStreamProto",ctypes.c_byte),  # 是否支持多码流，按位表示，位与结果：0-不支持，1-支持
        ("byStartDChan",ctypes.c_byte),  # 起始数字通道号，0表示无数字通道，比如DVR或IPC
        ("byStartDTalkChan",ctypes.c_byte),  # 起始数字对讲通道号，区别于模拟对讲通道号，0表示无数字对讲通道
        ("byHighDChanNum",ctypes.c_byte),  # 数字通道个数，高8位
        ("bySupport4",ctypes.c_byte),  # 能力集扩展，按位表示，位与结果：0- 不支持，1- 支持
        ("byLanguageType",ctypes.c_byte),  # 支持语种能力，按位表示，位与结果：0- 不支持，1- 支持
        ("byVoiceInChanNum",ctypes.c_byte),  # 音频输入通道数
        ("byStartVoiceInChanNo",ctypes.c_byte),  # 音频输入起始通道号，0表示无效
        ("bySupport5",ctypes.c_byte ),  # 按位表示,0-不支持,1-支持,bit0-支持多码流
        ("bySupport6",ctypes.c_byte),  # 按位表示,0-不支持,1-支持
        ("byMirrorChanNum",ctypes.c_byte),  # 镜像通道个数，录播主机中用于表示导播通道
        ("wStartMirrorChanNo", ctypes.c_uint16),  # 起始镜像通道号
        ("bySupport7",ctypes.c_byte),  # 能力,按位表示,0-不支持,1-支持
        ("byRes2",ctypes.c_byte)]  # 保留，置为0
LPNET_DVR_DEVICEINFO_V30 = ctypes.POINTER(NET_DVR_DEVICEINFO_V30)  

# 设备参数结构体 V40
class NET_DVR_DEVICEINFO_V40(ctypes.Structure):
    _fields_ = [
        ('struDeviceV30', NET_DVR_DEVICEINFO_V30),  # 设备信息
        ('bySupportLock',ctypes.c_byte),  # 设备支持锁定功能，该字段由SDK根据设备返回值来赋值的。bySupportLock为1时，dwSurplusLockTime和byRetryLoginTime有效
        ('byRetryLoginTime',ctypes.c_byte),  # 剩余可尝试登陆的次数，用户名，密码错误时，此参数有效
        ('byPasswordLevel',ctypes.c_byte),  # admin密码安全等级
        ('byProxyType',ctypes.c_byte),  # 代理类型，0-不使用代理, 1-使用socks5代理, 2-使用EHome代理
        ('dwSurplusLockTime',ctypes. c_uint32),  # 剩余时间，单位秒，用户锁定时，此参数有效
        ('byCharEncodeType',ctypes.c_byte),  # 字符编码类型
        ('bySupportDev5',ctypes.c_byte),  # 支持v50版本的设备参数获取，设备名称和设备类型名称长度扩展为64字节
        ('bySupport',ctypes.c_byte),   # 能力集扩展，位与结果：0- 不支持，1- 支持
        ('byLoginMode',ctypes.c_byte),  # 登录模式:0- Private登录，1- ISAPI登录
        ('dwOEMCode',ctypes. c_uint32),  # OEM Code
        ('iResidualValidity',ctypes. c_uint32),  # 该用户密码剩余有效天数，单位：天，返回负值，表示密码已经超期使用，例如“-3表示密码已经超期使用3天”
        ('byResidualValidity',ctypes.c_byte),  # iResidualValidity字段是否有效，0-无效，1-有效
        ('bySingleStartDTalkChan',ctypes.c_byte),  # 独立音轨接入的设备，起始接入通道号，0-为保留字节，无实际含义，音轨通道号不能从0开始
        ('bySingleDTalkChanNums',ctypes.c_byte),  # 独立音轨接入的设备的通道总数，0-表示不支持
        ('byPassWordResetLevel',ctypes.c_byte),  # 0-无效，
        # 1- 管理员创建一个非管理员用户为其设置密码，该非管理员用户正确登录设备后要提示“请修改初始登录密码”，未修改的情况下，用户每次登入都会进行提醒；
        # 2- 当非管理员用户的密码被管理员修改，该非管理员用户再次正确登录设备后，需要提示“请重新设置登录密码”，未修改的情况下，用户每次登入都会进行提醒。
        ('bySupportStreamEncrypt',ctypes.c_byte),  # 能力集扩展，位与结果：0- 不支持，1- 支持
        # bySupportStreamEncrypt & 0x1 表示是否支持RTP/TLS取流
        # bySupportStreamEncrypt & 0x2 表示是否支持SRTP/UDP取流
        # bySupportStreamEncrypt & 0x4 表示是否支持SRTP/MULTICAST取流
        ('byMarketType',ctypes.c_byte),  # 0-无效（未知类型）,1-经销型，2-行业型
        ('byRes2',ctypes.c_byte * 238)  #保留，置为0
    ]
LPNET_DVR_DEVICEINFO_V40 = ctypes.POINTER(NET_DVR_DEVICEINFO_V40)

fLoginResultCallBack = ctypes.CFUNCTYPE(None,ctypes. c_uint32,ctypes. c_uint32, LPNET_DVR_DEVICEINFO_V30, ctypes.c_void_p)

# NET_DVR_Login_V40()参数
class NET_DVR_USER_LOGIN_INFO(ctypes.Structure):
    _fields_ = [
        ("sDeviceAddress", ctypes.c_char * 129),  # 设备地址，IP 或者普通域名
        ("byUseTransport",ctypes.c_byte),  # 是否启用能力集透传：0- 不启用透传，默认；1- 启用透传
        ("wPort", ctypes.c_uint16),  # 设备端口号，例如：8000
        ("sUserName",ctypes.c_char * 64),  # 登录用户名，例如：admin
        ("sPassword", ctypes.c_char * 64),  # 登录密码g，例如：12345
        ("cbLoginResult", fLoginResultCallBack),  # 登录状态回调函数，bUseAsynLogin 为1时有效
        ("pUser", ctypes.c_void_p),  # 用户数据
        ("bUseAsynLogin",ctypes. c_uint32),  # 是否异步登录：0- 否，1- 是
        ("byProxyType",ctypes.c_byte),  # 0:不使用代理，1：使用标准代理，2：使用EHome代理
        ("byUseUTCTime",ctypes.c_byte),
        # 0-不进行转换，默认,1-接口上输入输出全部使用UTC时间,SDK完成UTC时间与设备时区的转换,2-接口上输入输出全部使用平台本地时间，SDK完成平台本地时间与设备时区的转换
        ("byLoginMode",ctypes.c_byte),  # 0-Private 1-ISAPI 2-自适应
        ("byHttps",ctypes.c_byte),  # 0-不适用tls，1-使用tls 2-自适应
        ("iProxyID",ctypes. c_uint32),  # 代理服务器序号，添加代理服务器信息时，相对应的服务器数组下表值
        ("byVerifyMode",ctypes.c_byte),  # 认证方式，0-不认证，1-双向认证，2-单向认证；认证仅在使用TLS的时候生效;
        ("byRes2",ctypes.c_byte * 119)]
LPNET_DVR_USER_LOGIN_INFO = ctypes.POINTER(NET_DVR_USER_LOGIN_INFO)

# 组件库加载路径信息
class NET_DVR_LOCAL_SDK_PATH(ctypes.Structure):
    pass
LPNET_DVR_LOCAL_SDK_PATH = ctypes.POINTER(NET_DVR_LOCAL_SDK_PATH)
NET_DVR_LOCAL_SDK_PATH._fields_ = [
    ('sPath', ctypes.c_char * 256),  # 组件库地址
    ('byRes',ctypes.c_byte * 128),
]

# 定义预览参数结构体
class NET_DVR_PREVIEWINFO(ctypes.Structure):
    pass
LPNET_DVR_PREVIEWINFO = ctypes.POINTER(NET_DVR_PREVIEWINFO)
NET_DVR_PREVIEWINFO._fields_ = [
    ('lChannel',ctypes. c_uint32),  # 通道号
    ('dwStreamType',ctypes. c_uint32),  # 码流类型，0-主码流，1-子码流，2-码流3，3-码流4, 4-码流5,5-码流6,7-码流7,8-码流8,9-码流9,10-码流10
    ('dwLinkMode',ctypes. c_uint32),  # 0：TCP方式,1：UDP方式,2：多播方式,3 - RTP方式，4-RTP/RTSP,5-RSTP/HTTP ,6- HRUDP（可靠传输） ,7-RTSP/HTTPS
    ('hPlayWnd', ctypes.c_void_p),  # 播放窗口的句柄,为NULL表示不播放图象
    ('bBlocked',ctypes. c_uint32),  # 0-非阻塞取流, 1-阻塞取流, 如果阻塞SDK内部connect失败将会有5s的超时才能够返回,不适合于轮询取流操作
    ('bPassbackRecord',ctypes. c_uint32),  # 0-不启用录像回传,1启用录像回传
    ('byPreviewMode', ctypes.c_ubyte),  # 预览模式，0-正常预览，1-延迟预览
    ('byStreamID', ctypes.c_ubyte * 32),  # 流ID，lChannel为0xffffffff时启用此参数
    ('byProtoType', ctypes.c_ubyte),  # 应用层取流协议，0-私有协议，1-RTSP协议,
    # 2-SRTP码流加密（对应此结构体中dwLinkMode 字段，支持如下方式, 为1，表示udp传输方式，信令走TLS加密，码流走SRTP加密，为2，表示多播传输方式，信令走TLS加密，码流走SRTP加密）
    ('byRes1', ctypes.c_ubyte),
    ('byVideoCodingType', ctypes.c_ubyte),  # 码流数据编解码类型 0-通用编码数据 1-热成像探测器产生的原始数据
    ('dwDisplayBufNum',ctypes. c_uint32),  # 播放库播放缓冲区最大缓冲帧数，范围1-50，置0时默认为1
    ('byNPQMode', ctypes.c_ubyte),  # NPQ是直连模式，还是过流媒体：0-直连 1-过流媒体
    ('byRecvMetaData', ctypes.c_ubyte),  # 是否接收metadata数据
    # 设备是否支持该功能通过GET /ISAPI/System/capabilities 中DeviceCap.SysCap.isSupportMetadata是否存在且为true
    ('byDataType', ctypes.c_ubyte),  # 数据类型，0-码流数据，1-音频数据
    ('byRes', ctypes.c_ubyte * 213),
]

#定义JPEG图像信息结构体
class NET_DVR_JPEGPARA(ctypes.Structure):
    pass
LPNET_DVR_JPEGPARA = ctypes.POINTER(NET_DVR_JPEGPARA)
NET_DVR_JPEGPARA._fields_ = [
    ('wPicSize', ctypes.c_ushort),
    ('wPicQuality', ctypes.c_ushort),
]

# 叠加字符
class NET_DVR_SHOWSTRINGINFO(ctypes.Structure):
    pass
LPNET_DVR_SHOWSTRINGINFO = ctypes.POINTER(NET_DVR_SHOWSTRINGINFO)
NET_DVR_SHOWSTRINGINFO._fields_ = [
    ('wShowString', ctypes.c_ushort),
    ('wStringSize', ctypes.c_ushort),
    ('wShowStringTopLeftX', ctypes.c_ushort),
    ('wShowStringTopLeftY', ctypes.c_ushort),
    ('sString', ctypes.c_ubyte * 44),
]

# 叠加字符
class NET_DVR_SHOWSTRING_V30(ctypes.Structure):
    pass
LPNET_DVR_SHOWSTRING_V30 = ctypes.POINTER(NET_DVR_SHOWSTRING_V30)
NET_DVR_SHOWSTRING_V30._fields_ = [
    ('dwSize',ctypes. c_uint32),
    ('struStringInfo', NET_DVR_SHOWSTRINGINFO * 8),
]

# 透传接口输出参数结构体
class NET_DVR_XML_CONFIG_OUTPUT(ctypes.Structure):
    pass
LPNET_DVR_XML_CONFIG_OUTPUT = ctypes.POINTER(NET_DVR_XML_CONFIG_OUTPUT)
NET_DVR_XML_CONFIG_OUTPUT._fields_ = [
    ('dwSize',ctypes. c_uint32),
    ('lpOutBuffer', ctypes.c_void_p),
    ('dwOutBufferSize',ctypes. c_uint32),
    ('dwReturnedXMLSize',ctypes. c_uint32),
    ('lpStatusBuffer', ctypes.c_void_p),
    ('dwStatusSize',ctypes. c_uint32),
    ('byRes', ctypes.c_ubyte * 32)
]

# 透传接口输入参数结构体
class NET_DVR_XML_CONFIG_INPUT(ctypes.Structure):
    pass
LPNET_DVR_XML_CONFIG_INPUT = ctypes.POINTER(NET_DVR_XML_CONFIG_INPUT)
NET_DVR_XML_CONFIG_INPUT._fields_ = [
    ('dwSize',ctypes. c_uint32),
    ('lpRequestUrl', ctypes.c_void_p),
    ('dwRequestUrlLen',ctypes. c_uint32),
    ('lpInBuffer', ctypes.c_void_p),
    ('dwInBufferSize',ctypes. c_uint32),
    ('dwRecvTimeOut',ctypes. c_uint32),
    ('byForceEncrpt', ctypes.c_ubyte),
    ('byNumOfMultiPart', ctypes.c_ubyte),
    ('byRes', ctypes.c_ubyte * 30)
]
# 时间参数结构体
class NET_DVR_TIME(ctypes.Structure):
    _fields_ = [
        ("dwYear",ctypes. c_uint32),  # 年
        ("dwMonth",ctypes. c_uint32),  # 月
        ("dwDay",ctypes. c_uint32),  # 日
        ("dwHour",ctypes. c_uint32),  # 时
        ("dwMinute",ctypes. c_uint32),  # 分
        ("dwSecond",ctypes. c_uint32)]  # 秒
LPNET_DVR_TIME = ctypes.POINTER(NET_DVR_TIME)

# IP地址结构体
class NET_DVR_IPADDR(ctypes.Structure):
    _fields_ = [
        ("sIpV4",ctypes.c_byte * 16),  # 设备IPv4地址
        ("sIpV6",ctypes.c_byte * 128)]  # 设备IPv6地址
LPNET_DVR_IPADDR = ctypes.POINTER(NET_DVR_IPADDR)

# 点坐标参数结构体
class NET_VCA_POINT(ctypes.Structure):
    _fields_ = [
        ("fX",ctypes.c_float),
        ("fY",ctypes.c_float)
]

# 日期信息结构体
class NET_DVR_DATE(ctypes.Structure):
    _fields_ = [
    ('wYear', ctypes.c_ushort),
    ('byMonth', ctypes.c_ubyte),
    ('byDay', ctypes.c_ubyte)
]

# 时间参数结构体
class NET_DVR_TIME(ctypes.Structure):
    _fields_ = [
        ("dwYear",ctypes. c_uint32),
        ("dwMonth",ctypes. c_uint32),
        ("dwDay",ctypes. c_uint32),
        ("dwHour",ctypes. c_uint32),
        ("dwMinute",ctypes. c_uint32),
        ("dwSecond",ctypes. c_uint32)
]
# 时间参数结构体
class NET_DVR_TIME_V30(ctypes.Structure):
    _fields_ = [
    ('wYear', ctypes.c_ushort),
    ('byMonth', ctypes.c_ubyte),
    ('byDay', ctypes.c_ubyte),
    ('byHour', ctypes.c_ubyte),
    ('byMinute', ctypes.c_ubyte),
    ('bySecond', ctypes.c_ubyte),
    ('byISO8601', ctypes.c_ubyte),
    ('wMilliSec', ctypes.c_ushort),
    ('cTimeDifferenceH', ctypes.c_ubyte),
    ('cTimeDifferenceM', ctypes.c_ubyte),
]

# IP地址结构体
class NET_DVR_IPADDR(ctypes.Structure):
    _fields_ = [
        ("sIpV4", ctypes.c_ubyte * 16),
        ("byIPv6", ctypes.c_ubyte * 128)]

class NET_DVR_ALARM_ISAPI_PICDATA(ctypes.Structure):
    _fields_ = [
        ("dwPicLen",ctypes. c_uint32),  # 图片数据长度
        ("byPicType", ctypes.c_ubyte),  # 图片格式: 1- jpg
        ("byRes", ctypes.c_ubyte * 3),  #
        ("szFilename", ctypes.c_ubyte * 256),  # 图片名称
        ("pPicData", ctypes.c_void_p),  # 图片数据
    ]
LPNET_DVR_ALARM_ISAPI_PICDATA = ctypes.POINTER(NET_DVR_ALARM_ISAPI_PICDATA)
class NET_DVR_LOCAL_GENERAL_CFG(ctypes.Structure):
    _fields_ = [
        ("byExceptionCbDirectly", ctypes.c_ubyte),  # 0-通过线程池异常回调，1-直接异常回调给上层
        ("byNotSplitRecordFile", ctypes.c_ubyte),  # 回放和预览中保存到本地录像文件不切片 0-默认切片，1-不切片
        ("byResumeUpgradeEnable", ctypes.c_ubyte),  # 断网续传升级使能，0-关闭（默认），1-开启
        ("byAlarmJsonPictureSeparate", ctypes.c_ubyte),  # 控制JSON透传报警数据和图片是否分离，0-不分离，1-分离（分离后走COMM_ISAPI_ALARM回调返回）
        ("byRes", ctypes.c_ubyte * 4),  # 保留
        ("i64FileSize", ctypes.c_uint64),  # 单位：Byte
        ("dwResumeUpgradeTimeout",ctypes. c_uint32),  # 断网续传重连超时时间，单位毫秒
        ("byAlarmReconnectMode", ctypes.c_ubyte),  # 0-独立线程重连（默认） 1-线程池重连
        ("byStdXmlBufferSize", ctypes.c_ubyte),  # 设置ISAPI透传接收缓冲区大小，1-1M 其他-默认
        ("byMultiplexing", ctypes.c_ubyte),  # 0-普通链接（非TLS链接）关闭多路复用，1-普通链接（非TLS链接）开启多路复用
        ("byFastUpgrade", ctypes.c_ubyte),  # 0-正常升级，1-快速升级
        ("byRes1", ctypes.c_ubyte * 232),  # 预留
    ]
LPNET_DVR_LOCAL_GENERAL_CFG = ctypes.POINTER(NET_DVR_LOCAL_GENERAL_CFG)



q1 = queue.Queue(5)
q2 = queue.Queue(5)
q3 = queue.Queue(5)
q4 = queue.Queue(5)
q5 = queue.Queue(5)


def deel(a):
        del a
        print("ovo")
class UI_Main(QMainWindow,Ui_MainWindow):
    def __init__(self) -> None:
        
        super().__init__()
        self.setupUi(self)
        self.this_serial = serial.Serial()
        # 定时器用于刷新扫码枪
        self.timer_flash = QtCore.QTimer()
        self.timer_flash_time = QtCore.QTimer()
        # self.timer_rx = QtCore.QTimer()
        # 定义保存文件变量
        self.picturePath = 'F:\\' #gaigaigai
        # self.picturePath = 'E:\\'
        # self.picturePath = 'C:\\'
        # 发动机型号
        self.engineModel = ""
        
        self.get_plc()
        # 发动机数量
        self.enginecount = 0#扫描发动机台数计数
        #self.port_open()
        self.TCP_connect()
        #初始化显示摄像头
        self.init_camera()
        # 初始化状态信息以及路径显示
        self.init_display()
        # 初始化槽函数
        self.solt_init()
        # 初始化定时器
        self.timer_flash.start(500)
        self.timer_flash_time.start(1000)
        self.textBrowser_6.setText("正常")
        self.label_12.setStyleSheet(
            "background-color:  rgb(0, 234, 0);border-radius: 27px; border: 3px groove gray;border-style: outset")
        # self.strx = {'DHP13':1, 'DHP15':2, 'DHP0':3}
        self.strx = {'DHP15':2, 'DHP0':3}
        self.str3 = 'DHP15'
        self.str4 = 'DHP0'
        self.count()
    def close_sys(self):
            os._exit(0)
    #重写closeEvent函数，窗口关闭时自动调用closeEvent函数
    def closeEvent(self,event):#窗口关闭时的弹出框
        reply = QtWidgets.QMessageBox.question(self,'提示','确认退出？',QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            event.accept()
            os._exit(0)
        else:
            event.ignore()
##########################



######################
    def init_camera(self):#初始化摄像头和IP，并启动多线程进行图像获取和显示
         self.Camera1 = Camera('rtsp://admin:abcd1234@192.168.1.64:554/h264/ch1/av_stream', self.label_2,q1)
         # self.Camera1 = Camera(0, self.label_2, self.textBrowser_2)
         self.Camera2 = Camera('rtsp://admin:abcd1234@192.168.1.74:554/h264/ch1/av_stream', self.label_3, q2)
         self.Camera3 = Camera('rtsp://admin:abcd1234@192.168.1.84:554/h264/ch1/av_stream', self.label_4, q3)
         self.Camera4 = Camera('rtsp://admin:abcd1234@192.168.1.94:554/h264/ch1/av_stream', self.label_10, q4)
         self.Camera5 = Camera('rtsp://admin:abcd1234@192.168.1.104:554/h264/ch1/av_stream', self.label_11, q5)
         self.all_cameras = [self.Camera1, self.Camera2,self.Camera3, self.Camera4,self.Camera5]
         for camera in self.all_cameras:
                def connect_lambda(cam):
                    return lambda lab,frame:camera.show(lab,frame)
                camera.send_data.connect(connect_lambda(camera))
         threading.Thread(target=self.Camera1.image_get).start()#线程使用，启动线程，多线程同时运行，提高程序运行效率
         threading.Thread(target=self.Camera3.image_get).start()
         threading.Thread(target=self.Camera4.image_get).start()
         threading.Thread(target=self.Camera5.image_get).start()
         threading.Thread(target=self.Camera2.image_get).start()
         threading.Thread(target=self.Camera2.image_show).start()
         threading.Thread(target=self.Camera1.image_show).start()
         threading.Thread(target=self.Camera3.image_show).start()
         threading.Thread(target=self.Camera4.image_show).start()
         threading.Thread(target=self.Camera5.image_show).start()

         
         threading.Thread(target=self.Camera5.camera_11()).start()
         threading.Thread(target=self.Camera4.camera_22()).start()
    def init_display(self):#展示发动机数量和图片保存路径
        sbsj= self.client.db_read(24, 20, 2)
        shi = get_usint(sbsj, 0)  # 解析第一个USInt值，偏移量为0
        fen = get_usint(sbsj, 1)
        formatted_time = f"{shi}点{fen}分"
        self.textBrowser_113.setText(formatted_time)

        kr = self.client.db_read(24, 4, 2)
        sll = int.from_bytes(kr[0:2], byteorder='big')
        self.enginecount = sll
        self.textBrowser_3.setText(str(self.enginecount))#textBrowser_3为发动机数量文本框
        self.textBrowser_4.setText(self.picturePath)#textBrowser_4为保存路径文本框

    # 获取扫码枪输入，并创建对应的文件夹保存图片，同时清空扫码枪输入
    def get_engineModel(self):
        if  self.textEdit.toPlainText().endswith('\n')  :  # 有以回车结束的输入，手动扫描枪获取到扫码信息，保存图片，计算发动机数量


            # if self.str3 in self.textBrowser_5.toPlainText(): #改改
            #     self.Camera4.camera_111()
            #     self.Camera5.camera_111()
            # if self.str4 in self.textBrowser_5.toPlainText():
            #     self.Camera4.camera_222()
            #     self.Camera5.camera_222()
            

            strovo = self.textEdit.toPlainText().replace("\n", '')
            stringData = bytearray(len(strovo)+2)
            util.set_string(stringData, 0, strovo, len(strovo)+2)
            stringData[0] = 254
            self.client.db_write(10, 12, stringData)#展示发动机编号

            # 等待1秒，确保数据稳定
            time.sleep(1)
            # 从数据库中读取预设点信息
            datax = self.ctrl_client.db_read(10, 574, 2)
            # 将读取的预设点信息转换为整数
            preset_point = int.from_bytes(datax[0:2], byteorder='big')
            # 如果预设点为0，则设置为1
            if preset_point == 0 :
                preset_point = 1
            # 根据预设点信息控制摄像头进行拍照
            self.Camera4.camera_xxx(preset_point)
            self.Camera5.camera_xxx(preset_point)

            # 根据发动机型号创建文件夹，用于保存图片
            foldername = self.create_folder(self.picturePath, self.textEdit.toPlainText().split('\n')[0].replace('*', '#'))  # 建文件夹
            #
            # 向数据库中写入数据，初始化开始状态
            self.client.db_write(10, 10, int.to_bytes(0, 2, 'big')) # 初始化begin
            # 向数据库中写入数据，表示已经扫描到码，可以停止
            self.client.db_write(10, 8, int.to_bytes(1, 2, 'big'))  # 扫到码了，可以停下
            # 等待3秒，确保数据稳定
            time.sleep(3) # 改改 分手持扫描与机器扫描两种?
            # 向数据库中写入数据，表示接收扫码枪输入成功，绿灯亮起
            self.client.db_write(10, 4, int.to_bytes(1, 2, 'big'))  # 接收扫码枪输入成功绿灯
            #就是这
            # 向数据库中写入数据，表示可以停止扫描
            self.client.db_write(10, 8, int.to_bytes(0, 2, 'big'))
            # 从数据库中读取停止扫描的指令
            data1 = self.client.db_read(10, 8, 2)
            # 将读取的停止扫描指令转换为整数
            self.stop1_int = int.from_bytes(data1[0:2], byteorder='big')
            
            if (self.stop1_int == 0):  # 拍照程序
                # abandoned
                if self.Camera1.flag:  # 若摄像头打开，保存图片类型，保存图片尺寸
                    cv2.imencode('.png', self.Camera1.saveframe)[1].tofile(foldername +  "\\"+ "图1_发动机顶部.png")
                if self.Camera2.flag:
                    cv2.imencode('.png', self.Camera2.saveframe)[1].tofile(foldername +  "\\"+"图2_发动机前侧.png")
                if self.Camera3.flag:
                    cv2.imencode('.png', self.Camera3.saveframe)[1].tofile(foldername + "\\"+ "图3_发动机后侧.png")
                if self.Camera4.flag:
                    cv2.imencode('.png', self.Camera4.saveframe)[1].tofile(foldername + "\\" +"图4_发动机铭牌.png")
                if self.Camera5.flag:
                    cv2.imencode('.png', self.Camera5.saveframe)[1].tofile(foldername + "\\" +"图5_发动机机身.png")
                 # if self.Camera9.flag:
                #     cv2.imencode('.png', self.Camera9.saveframe)[1].tofile(foldername + "\\" + "图9_发动机机身.png")
                # if self.Camera10.flag:
                #     cv2.imencode('.png', self.Camera10.saveframe)[1].tofile(foldername + "\\" + "图10_发动机机身.png")
                textpath = foldername + "\\发动机型号" + '.txt'
                

                self.engineModel = self.textEdit.toPlainText()
                # self.engineModel = self.textEdit.toPlainText().split('-')[1]
                self.textBrowser_5.setText(self.engineModel)
                textpath = foldername + "\\" + self.textBrowser_5.toPlainText().split('\n')[0].replace('*','#') + '.txt'  ###.split()返回列表，[0]第一维度去[]
                file = open(textpath, 'w')
                file.write(self.textBrowser_5.toPlainText())
                file.write('预置点: '+str(preset_point))
                file.close()

                self.textBrowser_2.setText(str(self.textBrowser_5.toPlainText().split('\n')[0]) + '\n' + "保存成功！")

                self.textEdit.clear()
                self.client.db_write(10, 10, int.to_bytes(1, 2, 'big'))
                self.enginecount += 1
                self.textBrowser_3.setText(str(self.enginecount))
        try:
            # 设置客户端套接字的超时时间为0.1秒
            self.client_socket.settimeout(0.1)
            # 接收客户端套接字的数据
            data2 = self.client_socket.recv(1024)
            # 打印接收到的数据
            print("Received data:", data2.decode())
            # 将接收到的数据设置到文本浏览器中
            self.textBrowser_5.setText(str(data2.decode()))
            # 去除文本浏览器中的换行符
            strov0 = self.textBrowser_5.toPlainText().replace("\n", '')
            # 创建一个字节数组，长度为字符串长度加2
            stringData = bytearray(len(strov0)+2)
            # 将字符串数据设置到字节数组中
            util.set_string(stringData, 0, strov0, len(strov0)+2)
            # 设置字节数组的第一个字节为254
            stringData[0] = 254
            # 将字节数组写入数据库
            self.client.db_write(10, 12, stringData)#展示发动机编号
            # 等待1秒
            time.sleep(1)
        except :
            # 如果发生异常，返回
            return

        """
        如果 textBrowser_5 的文本内容以 '*01' 结尾，则执行以下操作：
        1. 设置布尔值为 True，并将其写入数据库。
        2. 等待 1 秒。
        3. 从数据库中读取数据。
        4. 解析读取到的数据，获取发动机编号和预设点。
        5. 打印发动机编号。

        参数:
        无

        返回:
        无
        """
        # 判断 textBrowser_5 的文本内容是否以 '*01' 结尾
        if  self.textBrowser_5.toPlainText().endswith('*01') :
            # 创建一个字节数组，长度为 1
            boolData = bytearray(1)
            # 设置字节数组的第一个字节为 True
            util.set_bool(boolData, 0, 0, True)
            # 将布尔值写入数据库
            self.ctrl_client.db_write(10, 990, boolData)

            # 等待 1 秒
            time.sleep(1)
            # 从数据库中读取数据
            datax = self.ctrl_client.db_read(10, 574, 2)
            datay = self.ctrl_client.db_read(10, 14, 254)
            # 解析读取到的数据，获取发动机编号
            EngineNumber = datay.decode(encoding="ascii").strip(b'\x00'.decode())
            # 打印发动机编号
            print('111111')
            print(EngineNumber)
            # 从读取的数据中获取预设点
            preset_point = int.from_bytes(datax[0:2], byteorder='big')

            

            if preset_point == 0 :
                preset_point = 1
            self.Camera4.camera_xxx(preset_point)  # 传
            self.Camera5.camera_xxx(preset_point)

            # if self.str3 in self.textBrowser_5.toPlainText(): #改改 
               
            #     self.Camera4.camera_111()
            #     self.Camera5.camera_111()
            # if self.str4 in self.textBrowser_5.toPlainText():
            #     self.Camera4.camera_222()
            #     self.Camera5.camera_222()
               
            #print('自动扫描')
            foldername = self.create_folder(self.picturePath,self.textBrowser_5.toPlainText().split('\n')[0].replace('*', '#')
                                            )  # 建文件夹
            
            # 向数据库 10 的地址 4 写入一个 2 字节的整数 1，代表接收扫码枪输入成功，绿灯亮起
            self.client.db_write(10, 4, int.to_bytes(1, 2, 'big'))
            print('停下')
            # 向数据库 10 的地址 8 写入一个 2 字节的整数 1，代表拍照成功，给 PLC 信号
            self.client.db_write(10, 8, int.to_bytes(1, 2, 'big'))

            # 从数据库 10 的地址 572 读取 2 个字节的数据
            datax = self.ctrl_client.db_read(10, 572, 2)
            # 将读取到的 2 个字节数据转换为整数，作为睡眠时间
            sleep_time = int.from_bytes(datax[0:2], byteorder='big')
            # 等待一段时间，确保系统稳定
            time.sleep(max(sleep_time-4.5, 1))

            # 以下两行代码为测试用，实际使用时应注释或删除
            # self.client.db_write(10, 8, int.to_bytes(0, 2, 'big'))
            # data1 = self.client.db_read(10, 8, 2)
            # self.stop1_int = int.from_bytes(data1[0:2],byteorder='big')
            # 将 stop1_int 重置为 0
            self.stop1_int=0

            # 创建一个字节数组，长度为 1
            boolData = bytearray(1)
            # 设置字节数组的第一个字节为 False
            util.set_bool(boolData, 0, 0, False)
            # 将布尔值写入数据库 10 的地址 990
            self.ctrl_client.db_write(10, 990, boolData)


            if self.stop1_int==0 :#拍照程序
                # abandoned
                if self.Camera1.flag:  # 若摄像头打开，保存图片类型，保存图片尺寸
                    cv2.imencode('.png', self.Camera1.saveframe)[1].tofile(foldername + "\\"+"图1_发动机顶部.png")
                if self.Camera2.flag:
                    cv2.imencode('.png', self.Camera2.saveframe)[1].tofile(foldername + "\\" +"图2_发动机前侧.png")
                if self.Camera3.flag:
                    cv2.imencode('.png', self.Camera3.saveframe)[1].tofile(foldername + "\\" +"图3_发动机后侧.png")
                if self.Camera4.flag:
                    cv2.imencode('.png', self.Camera4.saveframe)[1].tofile(foldername + "\\" +"图4_发动机铭牌.png")
                if self.Camera5.flag:
                    cv2.imencode('.png',self.Camera5.saveframe)[1].tofile(foldername + "\\" +"图5_发动机-机身.png")
                textpath = foldername + "\\"+self.textBrowser_5.toPlainText().split('\n')[0].replace('*', '#') + '.txt'  ###.split()返回列表，[0]第一维度去[]
                file = open(textpath,'w')
                file.write(self.textBrowser_5.toPlainText())
                file.write('预置点: '+str(preset_point))
                file.close()
                self.client.db_write(10, 10, int.to_bytes(1, 2, 'big'))#

                self.textBrowser_2.setText(str(self.textBrowser_5.toPlainText().split('\n')[0])+'\n'+"保存成功！")
                print(str(self.textBrowser_5.toPlainText().split('\n')[0])+'\n'+"保存成功！")
                self.textEdit.clear()
                self.client.db_write(10, 10, int.to_bytes(1, 2, 'big'))
                self.client.db_write(10, 10, int.to_bytes(0, 2, 'big'))
                self.enginecount += 1
                self.textBrowser_3.setText(str(self.enginecount))
        else:
            
            return
        if self.client.get_connected():  # self.textEdit.toPlainText()获取的是textEdit中输入的文本
                db = 10
                data = self.client.db_read(int(db), 0, 10)

                self.senor_Int= int.from_bytes(data[0:2], byteorder='big')  #####1
                self.warning_Int = int.from_bytes(data[2:4], byteorder='big')  ####2
                self.san_int = int.from_bytes(data[4:6], byteorder='big')
                self.si_int = int.from_bytes(data[6:8], byteorder='big')
                self.stop_int = int.from_bytes(data[8:10], byteorder='big')
                self.begin_int = int.from_bytes(data[10:12], byteorder='big')
                #
                if  self.textBrowser_5.toPlainText().endswith('*01'):
                    self.client.db_write(10, 0,  int.to_bytes(1, 2, 'big'))
                    senor_Int= self.client.db_read(int(db), 0, 2)
                    self.senor_Int = int.from_bytes(senor_Int[0:2], byteorder='big')
                #
                # plc传感器输出为0并且手动扫描文本框为空时报警
                if self.senor_Int == 0 and self.textEdit.toPlainText() == ' ':
                    self.client.db_write(int(db), 2, int.to_bytes(1, 2, 'big'))
                    #
                    self.client.db_write(int(db), 6, int.to_bytes(1, 2, 'big'))#接收失败红灯
                    #
                    self.textBrowser_6.setText("异常")#报警模块报警
                    self.label_12.setStyleSheet(
                        "background-color: red;border-radius: 30px; border: 3px groove gray;border-style: outset")
                   #提示灯变红
                    #time.sleep(8)#8秒后取消报警
                    # self.client.db_write(int(db), 2, int.to_bytes(0, 2, 'big'))
                    #
                    self.client.db_write(int(db), 6, int.to_bytes(0, 2, 'big'))#取消报警绿灯
                    #
                    self.label_12.setStyleSheet(
                        "background-color:  rgb(0, 234, 0);border-radius: 30px; border: 3px groove gray;border-style: outset")
                    self.textBrowser_6.setText("正常")
                # elif self.senor_Bool==0 and self.textEdit.toPlainText()!=' ':
                # elif self.senor_Bool==1 and self.textEdit.toPlainText()!=' ':

    #创建文件夹
    def create_folder(self,path,encode):
        year = datetime.now().strftime('%Y')
        month = datetime.now().strftime('%Y-%m')
        day = datetime.now().strftime('%Y-%m-%d')
        hour = datetime.now().strftime("%H-%M-%S-%f")[:12]
        foldername2 = path + "\\" + year + "\\" + month + "\\" + day
        # if not os.path.exists(foldername2):
        #     self.enginecount = 0
        #     self.textBrowser_3.setText(str(self.enginecount))
        # foldername = path + "\\" + year + "\\" + month + "\\" + day + "\\" +self.textBrowser_5.toPlainText().replace('*', '#')
        foldername = path + "\\" + year + "\\" + month + "\\" + day + "\\"+encode
        if not os.path.exists(foldername):
            os.makedirs(foldername)
        return foldername
    def get_plc(self):#连接plc
        self.client = snap7.client.Client()
        self.ctrl_client = snap7.client.Client()
        try:
            self.client.connect('192.168.2.30', 0, 0)
            self.ctrl_client.connect('192.168.2.30', 0, 0)
            if self.client.get_connected() and self.ctrl_client.get_connected():
                print('PLC连接成功')
                self.textBrowser_610.setText("正常")
                self.label_620.setStyleSheet(
                    "background-color: rgb(0, 234, 0);border-radius: 27px; border: 3px groove gray;border-style: outset")
        except:
            print('PLC连接失败')
            self.textBrowser_610.setText("异常")#textBrowser_610为plc模块文本框
    def TCP_connect(self):
        self.host = "192.168.1.100"  # 设备的 IP 地址
        self.port = 51236  # 设备的端口号
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.client_socket.connect((self.host, self.port))
            print("Connected to", self.host, "on port", self.port)
            self.client_socket.settimeout(0.2)
            self.textBrowser_7.setText("正常")  # textBrowser_7为数据模块文本框
            self.label_15.setStyleSheet(
                                "background-color: rgb(0, 234, 0);border-radius: 27px; border: 3px groove gray;border-style: outset")
            #label_15为数据模块文本框旁边的指示灯

        except :
            # print("Connection timed out")
            self.textBrowser_2.setText("TCP未连接")  # textBrowser_2为结果状态信息文本框
            self.textBrowser_7.setText("异常")
            self.label_15.setStyleSheet(
                "background-color: red;border-radius: 27px; border: 3px groove gray;border-style: outset")
            # label_15为数据模块文本框旁边的指示灯

            return
    #按钮按下，实现保存路径的选择
    def openPath_button(self):
        # fileName = QtWidgets.QFileDialog.getExistingDirectory(None,"选择图片保存路径","E:\\")  # gaigaigai
        fileName = QtWidgets.QFileDialog.getExistingDirectory(None, "选择图片保存路径", "F:\\")
        self.picturePath = fileName
        self.textBrowser_4.setText(fileName)
        if self.picturePath == "":#用不到
            self.picturePath = "F:\\"  # gaigaigai
            # self.picturePath = "E:\\"
        if self.textBrowser_4.toPlainText() == "":#若被删除路径，采用默认路径
            self.textBrowser_4.setText(self.picturePath)

    def openToday_button(self): #查看路径
        year = datetime.now().strftime('%Y')
        month = datetime.now().strftime('%Y-%m')
        day = datetime.now().strftime('%Y-%m-%d')
        todaypath = self.picturePath + '\\' + year + '\\' + month + '\\' + day
        #fileName = QtWidgets.QFileDialog.getOpenFileName(None, "查看当天路径", todaypath,"ALL Files(*);;Text Files(*.txt)")
        if not os.path.exists(todaypath):
            os.makedirs(todaypath)
        try:
            os.startfile(todaypath)
        except:pass
    def off_warning_button(self):#取消报警
        self.textBrowser_6.setText("正常")#textBrowser_6为报警模块
        self.label_12.setStyleSheet(
            "background-color: rgb(0, 234, 0);border-radius: 27px; border: 3px groove gray;border-style: outset")
        if self.client.get_connected():  # self.textEdit.toPlainText()获取的是textEdit中输入的文本
            self.client.db_write(10, 2, int.to_bytes(0, 2, 'big'))#取消报警为0
            #
            # self.client.db_write(10, 6, int.to_bytes(0, 2, 'big'))#取消报警，接收失败报警红灯取消
            #
    def reflesh_data_button(self):#刷新
        #self.port_open()
        self.get_plc()
        self.TCP_connect()
        year = datetime.now().strftime('%Y')
        month = datetime.now().strftime('%Y-%m')
        day = datetime.now().strftime('%Y-%m-%d')
        path = self.picturePath + '\\' + year + '\\' + month + '\\' + day
        files = os.listdir(path)   # 读入文件夹
        num_png = len(files)       # 统计文件夹中的文件个数
        kr = self.client.db_read(24, 4, 2)
        sll = int.from_bytes(kr[0:2], byteorder='big')
        self.enginecount = sll
        self.textBrowser_3.setText(str(self.enginecount))#textBrowser_3为发动机数量文本框

    #显示时间
    def show_time(self):#显示时间
        datetime = QtCore.QDateTime.currentDateTime()#获取当前时间
        text = datetime.toString('yyyy/MM/dd  HH:mm:ss  dddd')#将时间格式化为字符串输出
        self.label_9.setText(" " + text)#时间星期输出到label_9上
    def count(self):
        year = datetime.now().strftime('%Y')
        month = datetime.now().strftime('%Y-%m')
        day = datetime.now().strftime('%Y-%m-%d')
        foldername1 = self.picturePath + "\\" + year + "\\" + month + "\\" + day

        if not os.path.exists(foldername1):
            print('创建')
            os.makedirs(foldername1)
        path = self.picturePath + '\\' + year + '\\' + month + '\\' + day

        files = os.listdir(path)  # 读入文件夹
        self.num_png = len(files)  # 统计文件夹中的文件个数
        kr = self.client.db_read(24, 4, 2)
        sll = int.from_bytes(kr[0:2], byteorder='big')
        self.enginecount = sll
        self.textBrowser_3.setText(str(self.enginecount))#textBrowser_3为发动机数量文本框
    #初始化槽函数
    def solt_init(self):
        self.pushButton.clicked.connect(self.openPath_button)
        self.pushButton_2.clicked.connect(self.openToday_button)
        self.pushButton_3.clicked.connect(self.reflesh_data_button)
        self.pushButton_4.clicked.connect(self.off_warning_button)
        self.pushButton_5.clicked.connect(self.close_sys)
        self.timer_flash.timeout.connect(self.get_engineModel)#定时刷新得到扫描信息功能
        # self.timer_rx.timeout.connect(self.read_data)
        self.timer_flash_time.timeout.connect(self.show_time)


#相机类，用来获取IP摄像头的流媒体数据
class Camera(QThread):
    #类属性，用来标识当前摄像头个数
    camera_count = 1
    send_data= pyqtSignal(object,object)
    #初始化对象，对象有url，输出框，状态框三个属性
    def __init__(self,url,  out_label,q):
        '''
        初始化相机线程对象
        参数：
            url：相机的URL地址
            out_label：用于显示图像的标签
            q：用于存储图像数据的队列
        '''
        # 调用父类的构造函数进行初始化
        super().__init__()
        # 初始化相机的URL地址
        self.url =url
        # 初始化用于显示图像的标签
        self.out_label = out_label##
        # 初始化相机的计数
        self.count = self.camera_count
        # 类属性，用于记录已创建的相机线程对象数量
        self.__class__.camera_count += 1
        # 初始化标志位，用于控制线程的运行状态
        self.flag = False
        # 初始化用于存储图像数据的队列
        self.q=q
        # 初始化相机图像的保存路径
        self.dir = r'F:\成套下线测试\lib'

        # self.dir = r'D:\成套下线\环境\lib'  # gaigaigai
        # self.dir = r'C:\Users\meng\Desktop\西港项目\finally\lib'
    def image_get(self):#
        self.cap = cv2.VideoCapture(self.url)
        if self.cap.isOpened():#判断摄像头是否开启，默认未开启
            self.flag = True
        else:
            self.status_label.append("摄像头" + str(self.count) + "未连接！")
        while True:#self.cap.isOpened():
            try:
                self.success, frame = self.cap.read()  # 是否成功，内容
                self.q.put(frame)
                self.saveframe = cv2.resize(frame, (1280, 720))#截取图片尺寸
            except Exception as e:
                # print(e)
                continue
            #self.saveframe = cv2.resize(frame, (1280, 720))#截取图片尺寸
    def image_show(self):
        while True:
            try:
                a = self.q.get()#block=True, timeout=100
                a.all!=None#self.q.qsize()>0:#####self.q.get(),self.q.get() !=None
                frame = a
                try:
                    frame = cv2.GaussianBlur(frame, (5, 5), 0)
                    # displayframe = cv2.resize(frame, (468, 324))

                    displayframe = cv2.resize(frame, (520, 360))
                    displayframe = cv2.cvtColor(displayframe,cv2.COLOR_BGR2RGB)
                    img = QtGui.QImage(displayframe.data, displayframe.shape[1], displayframe.shape[0],
                                   QtGui.QImage.Format_RGB888)
                    pixmap=QtGui.QPixmap.fromImage(img)
                    self.send_data.emit(self.out_label,pixmap)
                    # self.out_label.setPixmap(QtGui.QPixmap.fromImage(img))#输出图像##frame
                except Exception as e:
                    # print(e)
                    continue
            except Exception as e:
                # print(e)
                continue
    def show(self,lab,date):
        lab.setPixmap(date)
    def camera_33(self):
        os.chdir(self.dir)
        self.sdk = ctypes.CDLL(r'./HCNetSDK.dll')
        self.SetSDKInitCfg()  # 设置组件库和SSL库加载路径
        # 初始化
        self.sdk.NET_DVR_Init()
        # 启用SDK写日志
        self.sdk.NET_DVR_SetLogToFile(3, bytes('./SdkLog_Python/', encoding="utf-8"), False)
        # 通用参数配置
        sdkCfg = NET_DVR_LOCAL_GENERAL_CFG()
        sdkCfg.byAlarmJsonPictureSeparate = 1
        self.sdk.NET_DVR_SetSDKLocalCfg(17, ctypes.byref(sdkCfg))
        # 初始化用户id, 在调用正常是程序一般返回正数，故初始化一个负数
        self.UserID = ctypes.c_long(-1)
        # 用户注册设备
        # c++传递进去的是byte型数据，需要转成byte型传进去，否则会乱码
        # 登录参数，包括设备地址、登录用户、密码等
        struLoginInfo = NET_DVR_USER_LOGIN_INFO()
        struLoginInfo.bUseAsynLogin = 0  # 同步登录方式
        struLoginInfo.sDeviceAddress = bytes("192.168.1.114", "ascii")
        # struLoginInfo.sDeviceAddress = bytes("192.168.1.94", "ascii")
        struLoginInfo.wPort = 8000  # 设备服务端口
        struLoginInfo.sUserName = bytes("admin", "ascii")  # 设备登录用户名
        struLoginInfo.sPassword = bytes("abcd1234", "ascii")  # 设备登录密码
        struLoginInfo.byLoginMode = 0
        # 设备信息, 输出参数
        struDeviceInfoV40 = NET_DVR_DEVICEINFO_V40()
        self.UserID = self.sdk.NET_DVR_Login_V40(ctypes.byref(struLoginInfo), ctypes.byref(struDeviceInfoV40))

        if self.UserID < 0:
            print("Login failed, error code: %d" % self.sdk.NET_DVR_GetLastError())
            self.sdk.NET_DVR_Cleanup()
        else:
            print('登录成功，设备序列号：%s' % str(struDeviceInfoV40.struDeviceV30.sSerialNumber, encoding="utf8"))
            print("摄像头机身1")

    def camera_11(self):
        os.chdir(self.dir)
        self.sdk = ctypes.CDLL(r'./HCNetSDK.dll')
        self.SetSDKInitCfg()  # 设置组件库和SSL库加载路径
        # 初始化
        self.sdk.NET_DVR_Init()
        # 启用SDK写日志
        self.sdk.NET_DVR_SetLogToFile(3, bytes('./SdkLog_Python/', encoding="utf-8"), False)
        # 通用参数配置
        sdkCfg = NET_DVR_LOCAL_GENERAL_CFG()
        sdkCfg.byAlarmJsonPictureSeparate = 1
        self.sdk.NET_DVR_SetSDKLocalCfg(17, ctypes.byref(sdkCfg))
        # 初始化用户id, 在调用正常是程序一般返回正数，故初始化一个负数
        self.UserID = ctypes.c_long(-1)
        # 用户注册设备
        # c++传递进去的是byte型数据，需要转成byte型传进去，否则会乱码
        # 登录参数，包括设备地址、登录用户、密码等
        struLoginInfo = NET_DVR_USER_LOGIN_INFO()
        struLoginInfo.bUseAsynLogin = 0  # 同步登录方式
        struLoginInfo.sDeviceAddress = bytes("192.168.1.104", "ascii")
        # struLoginInfo.sDeviceAddress = bytes("192.168.1.94", "ascii")
        struLoginInfo.wPort = 8000  # 设备服务端口
        struLoginInfo.sUserName = bytes("admin", "ascii")  # 设备登录用户名
        struLoginInfo.sPassword = bytes("abcd1234", "ascii")  # 设备登录密码
        struLoginInfo.byLoginMode = 0
        # 设备信息, 输出参数
        struDeviceInfoV40 = NET_DVR_DEVICEINFO_V40()
        self.UserID = self.sdk.NET_DVR_Login_V40(ctypes.byref(struLoginInfo), ctypes.byref(struDeviceInfoV40))

        if self.UserID < 0:
            print("Login failed, error code: %d" % self.sdk.NET_DVR_GetLastError())
            self.sdk.NET_DVR_Cleanup()
        else:
            print('登录成功，设备序列号：%s' % str(struDeviceInfoV40.struDeviceV30.sSerialNumber, encoding="utf8"))
            print("摄像头铭牌")

    def camera_22(self):
        os.chdir(self.dir)
        self.sdk = ctypes.CDLL(r'./HCNetSDK.dll')
        self.SetSDKInitCfg()  # 设置组件库和SSL库加载路径
        # 初始化
        self.sdk.NET_DVR_Init()
        # 启用SDK写日志
        self.sdk.NET_DVR_SetLogToFile(3, bytes('./SdkLog_Python/', encoding="utf-8"), False)
        # 通用参数配置
        sdkCfg = NET_DVR_LOCAL_GENERAL_CFG()
        sdkCfg.byAlarmJsonPictureSeparate = 1
        self.sdk.NET_DVR_SetSDKLocalCfg(17, ctypes.byref(sdkCfg))
        # 初始化用户id, 在调用正常是程序一般返回正数，故初始化一个负数
        self.UserID = ctypes.c_long(-1)
        # 用户注册设备
        # c++传递进去的是byte型数据，需要转成byte型传进去，否则会乱码
        # 登录参数，包括设备地址、登录用户、密码等
        struLoginInfo = NET_DVR_USER_LOGIN_INFO()
        struLoginInfo.bUseAsynLogin = 0  # 同步登录方式
        struLoginInfo.sDeviceAddress = bytes("192.168.1.94", "ascii")
        # struLoginInfo.sDeviceAddress = bytes("192.168.1.94", "ascii")
        struLoginInfo.wPort = 8000  # 设备服务端口
        struLoginInfo.sUserName = bytes("admin", "ascii")  # 设备登录用户名
        struLoginInfo.sPassword = bytes("abcd1234", "ascii")  # 设备登录密码
        struLoginInfo.byLoginMode = 0
        # 设备信息, 输出参数
        struDeviceInfoV40 = NET_DVR_DEVICEINFO_V40()
        self.UserID = self.sdk.NET_DVR_Login_V40(ctypes.byref(struLoginInfo), ctypes.byref(struDeviceInfoV40))

        if self.UserID < 0:
            print("Login failed, error code: %d" % self.sdk.NET_DVR_GetLastError())
            self.sdk.NET_DVR_Cleanup()
        else:
            print('登录成功，设备序列号：%s' % str(struDeviceInfoV40.struDeviceV30.sSerialNumber, encoding="utf8"))
            print('摄像头机身')
    def camera_111(self):
        # 布防句柄
        # handle = c_long(-1)
        # sdk.NET_DVR_SetupAlarmChan_V41.restype = c_long
        iChannel = ctypes.c_long(1)  # 设备通道号
        dwPTZPresetCmd = ctypes.c_ulong(39)
        dwPresetIndex = ctypes.c_ulong(2)

        if self.sdk.NET_DVR_PTZPreset_Other(self.UserID, iChannel, dwPTZPresetCmd, dwPresetIndex) is None:
            print("PAN_LEFT start failed, error code: %d\n", self.sdk.NET_DVR_GetLastError())
            self.sdk.NET_DVR_Logout(self.UserID)
            self.sdk.NET_DVR_Cleanup()
        else:
            print("chenggong")
        # 注销用户，退出程序时调用
        # self.sdk.NET_DVR_Logout(self.UserID)
        # # 释放SDK资源，退出程序时调用
        # self.sdk.NET_DVR_Cleanup()

    def camera_222(self):  # 增加标定 
        # 布防句柄
        # handle = c_long(-1)
        # sdk.NET_DVR_SetupAlarmChan_V41.restype = c_long
        iChannel = ctypes.c_long(1)  # 设备通道号
        dwPTZPresetCmd = ctypes.c_ulong(39)
        dwPresetIndex = ctypes.c_ulong(3)

        if self.sdk.NET_DVR_PTZPreset_Other(self.UserID, iChannel, dwPTZPresetCmd, dwPresetIndex) is None:
            print("PAN_LEFT start failed, error code: %d\n", self.sdk.NET_DVR_GetLastError())
            self.sdk.NET_DVR_Logout(self.UserID)
            self.sdk.NET_DVR_Cleanup()
        else:
            print("chenggong")
        # 注销用户，退出程序时调用
        # self.sdk.NET_DVR_Logout(self.UserID)
        # # 释放SDK资源，退出程序时调用
        # self.sdk.NET_DVR_Cleanup()

    def camera_xxx(self, xxx):  # 增加标定 改改
        # 布防句柄
        # handle = c_long(-1)
        # sdk.NET_DVR_SetupAlarmChan_V41.restype = c_long
        iChannel = ctypes.c_long(1)  # 设备通道号
        dwPTZPresetCmd = ctypes.c_ulong(39)
        dwPresetIndex = ctypes.c_ulong(xxx)

        if self.sdk.NET_DVR_PTZPreset_Other(self.UserID, iChannel, dwPTZPresetCmd, dwPresetIndex) is None:
            print("PAN_LEFT start failed, error code: %d\n", self.sdk.NET_DVR_GetLastError())
            self.sdk.NET_DVR_Logout(self.UserID)
            self.sdk.NET_DVR_Cleanup()
        else:
            print("chenggong")
        # 注销用户，退出程序时调用
        # self.sdk.NET_DVR_Logout(self.UserID)
        # # 释放SDK资源，退出程序时调用
        # self.sdk.NET_DVR_Cleanup()

    def SetSDKInitCfg(self):
        # 设置HCNetSDKCom组件库和SSL库加载路径

        strPath = os.getcwd().encode('gbk')
        sdk_ComPath = NET_DVR_LOCAL_SDK_PATH()
        sdk_ComPath.sPath = strPath
        self.sdk.NET_DVR_SetSDKInitCfg(2, ctypes.byref(sdk_ComPath))
        self.sdk.NET_DVR_SetSDKInitCfg(3, ctypes.create_string_buffer(strPath + b'\libcrypto-1_1-x64.dll'))
        self.sdk.NET_DVR_SetSDKInitCfg(4, ctypes.create_string_buffer(strPath + b'\libssl-1_1-x64.dll'))


if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)  # 每个PyQt5应⽤都必须创建⼀个应⽤对象。sys.argv是⼀组命令⾏参数的列表。
        window = UI_Main()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print('发生异常：', e)
