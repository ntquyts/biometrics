# Metody biometryczne
# Przemyslaw Pastuszka

from PIL import Image, ImageDraw
import math
import sobel
import copy

def apply_kernel_at(get_value, kernel, i, j):
    kernel_size = len(kernel)
    result = 0
    for k in range(0, kernel_size):
        for l in range(0, kernel_size):
            pixel = get_value(i + k - kernel_size / 2, j + l - kernel_size / 2)
            result += pixel * kernel[k][l]
    return result

def apply_to_each_pixel(pixels, f):
    for i in range(0, len(pixels)):
        for j in range(0, len(pixels[i])):
            pixels[i][j] = f(pixels[i][j])

def calculate_angles(im, W, f, g):
    (x, y) = im.size
    im_load = im.load()
    get_pixel = lambda x, y: im_load[x, y]

    ySobel = sobel.sobelOperator
    xSobel = sobel.transpose(sobel.sobelOperator)

    result = [[] for i in range(1, x, W)]

    for i in range(1, x, W):
        for j in range(1, y, W):
            nominator = 0
            denominator = 0
            for k in range(i, min(i + W , x - 1)):
                for l in range(j, min(j + W, y - 1)):
                    Gx = apply_kernel_at(get_pixel, xSobel, k, l)
                    Gy = apply_kernel_at(get_pixel, ySobel, k, l)
                    nominator += f(Gx, Gy)
                    denominator += g(Gx, Gy)
            angle = (math.pi + math.atan2(nominator, denominator)) / 2
            result[(i - 1) / W].append(angle)

    return result

def gauss(x, y):
    ssigma = 1.0
    return (1 / (2 * math.pi * ssigma)) * math.exp(-(x * x + y * y) / (2 * ssigma))

def gauss_kernel(size):
    kernel = [[] for i in range(0, size)]
    for i in range(0, size):
        for j in range(0, size):
            kernel[i].append(gauss(i - size / 2, j - size / 2))
    return kernel

def apply_kernel(pixels, kernel):
    size = len(kernel)
    for i in range(size / 2, len(pixels) - size / 2):
        for j in range(size / 2, len(pixels[i]) - size / 2):
            pixels[i][j] = apply_kernel_at(lambda x, y: pixels[x][y], kernel, i, j)

def smooth_angles(angles):
    cos_angles = copy.deepcopy(angles)
    sin_angles = copy.deepcopy(angles)
    apply_to_each_pixel(cos_angles, lambda x: math.cos(2 * x))
    apply_to_each_pixel(sin_angles, lambda x: math.sin(2 * x))

    kernel = gauss_kernel(5)
    apply_kernel(cos_angles, kernel)
    apply_kernel(sin_angles, kernel)

    for i in range(0, len(cos_angles)):
        for j in range(0, len(cos_angles[i])):
            cos_angles[i][j] = (math.atan2(sin_angles[i][j], cos_angles[i][j])) / 2

    return cos_angles

def radians_to_degrees(x):
    deg = math.degrees(x) % 360
    return deg

def calculate_singularities(angles, tolerance):
    apply_to_each_pixel(angles, lambda x: radians_to_degrees(x))
    # apply_kernel(angles, [[1, 1, 1], [1, 0, 1], [1, 1, 1]])

    for i in range(1, len(angles) - 1):
        for j in range(1, len(angles[i]) - 1):
            pixel = angles[i][j]
            if 180 - tolerance <= pixel and pixel <= 180 + tolerance:
                print i, j, "loop"
            if -180 - tolerance <= pixel and pixel <= -180 + tolerance:
                print i, j, "delta"
            if 360 - tolerance <= pixel and pixel <= 360 + tolerance:
                print i, j, "whorl"
            # print i, j, radians_to_degrees(pixel)

def draw_lines(im, angles, W):
    (x, y) = im.size
    result = im.convert("RGB")

    draw = ImageDraw.Draw(result)

    for i in range(1, x, W):
        for j in range(1, y, W):
            tang = math.tan(angles[(i - 1) / W][(j - 1) / W])

            if -1 <= tang and tang <= 1:
                begin = (i, (-W/2) * tang + j + W/2)
                end = (i + W, (W/2) * tang + j + W/2)
            else:
                begin = (i + W/2 + W/(2 * tang), j + W/2)
                end = (i + W/2 - W/(2 * tang), j - W/2)

            draw.line([begin, end], fill=150)

    del draw

    return result