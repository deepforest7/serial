import serial
def getdata():#发送函数
    com = 10
    bsp = 9600
    x = serial.Serial(com, bsp)  # 这是我的串口，测试连接成功，没毛病
    #myinput= bytes([0X01,0X03,0X00,0X00,0X00,0X01,0X84,0X0A])
    myinput = bytes([0XAA, 0XA0, 0X00, 0X00, 0X00, 0X0A])
    #这是我要发送的命令，原本命令是：01 03 00 00 00 01 84 0A
    x.write(myinput)
    # AB A0 0D 00 00 25 02 BE 00 2D 03 50 00 6F 02 F8 74
    myout=x.read(17)#读取串口传过来的字节流，这里我根据文档只接收7个字节的数据
    datas =''.join(map(lambda x:('/x' if len(hex(x))>=4 else '/x0')+hex(x)[2:],myout))#将数据转成十六进制的形式
    new_datas = datas.split("/x")#将字符串分割，拼接下标4和5部分的数据
    need = new_datas[9] * 256 + new_datas[10];#need是拼接出来的数据，比如：001a
    #my_need = int(hex(int(need,16)),16)#将十六进制转化为十进制

    my_need = int(hex(int(new_datas[9], 16)), 16)* 256 + int(hex(int(new_datas[10],16)),16)


    print('mm:',my_need)



getdata()