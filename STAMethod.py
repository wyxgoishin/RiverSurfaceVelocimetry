import cv2
import numpy as np
from LinearPolar import RecTangle2Polar


def calTextureAngle(img, theta_num=360, norm=False, histEqualize=False):
    """
    采用自相关函数法（Fujita2018)计算输入图片的纹理角，首先将输入图像截取为正方形
    而后利用傅里叶变换快速计算图像的自相关函数。之后将自相关函数图片转换为极坐标表示形式，
    并利用梯形积分计算u(theta)，即每个角度对应的rou的积分值，而后取最大值模90作为
    纹理角的余角
        :param img: 输入图片，可为灰度图或BGR模式的图片
        :param theta_num: 转换为极坐标时的角度划分份数，默认为360份，即计算精度为1度
        :param norm: 是否对图片进行列标准化，在直方图均衡后进行
        :param histEqualize: 是否对图片进行直方图均衡
    :return:
    """
    if len(img.shape) > 2:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    if histEqualize:
        img = cv2.equalizeHist(img)

    if norm:
        mu = np.mean(img, axis=0)
        sigma = np.std(img, axis=0)
        img = (img - mu) / sigma

    # 截取图片为最大正方形
    length = min(img.shape[0], img.shape[1])
    img = img[0:length][0:length]

    # 计算自相关函数
    # A(x, y) = I(x, y) * I(x, y) = IFFT(|FFT{I(x,y)}|^2)
    # 即先对图片进行傅里叶变换，而后取模的平方做逆傅里叶变化，最后将其移动中心
    # 注意逆傅里叶变换得到的图片矩阵也是复数矩阵，也需要取模以方便后续操作
    img_f = np.fft.fft2(img)
    img_ac = abs(np.fft.fftshift(np.fft.ifft2(np.abs(img_f) ** 2)))
    # 归一化图片，使得图片中点的值变为1
    img_ac /= img_ac[length // 2][length // 2]
    # 最大模长为图片长度的一半，超出会报错，因为自定义函数里没写
    # OpenCV里的函数linearPolar()倒是可以随便定，因为会填充，但是没法自定义角度精度
    img_ac_polar = RecTangle2Polar(img_ac, [length // 2, theta_num])

    # 计算mu_theta，注意一定要360度全算，只算90度会出错，因此后续求纹理角前要模90
    mu_theta = {}
    for i in range(img_ac_polar.shape[0]):
        mu_theta[i] = sum(img_ac_polar[i, :]) - (img_ac_polar[i, 0] + img_ac_polar[i, img_ac_polar.shape[1] - 1]) / 2

    mu_theta = sorted(mu_theta.items(), key=lambda x: x[1], reverse=True)
    alpha = 90 - mu_theta[0][0] * 360 / theta_num % 90
    return alpha


real_alpha = 51.6
img = cv2.imread('sti_imgs/fai=%s.png' % str(real_alpha))
alpha = calTextureAngle(img, theta_num=720)
print("real_fai=%.2f, cal_fai=%.2f" % (real_alpha, alpha))
