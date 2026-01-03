from pygame import transform


def resize(image, scale):
    size = image.get_size()
    return transform.scale(image, (int(size[0] * scale), int(size[1] * scale)))


def resize_without_proportion(image, scale_x, scale_y):
    size = image.get_size()
    return transform.scale(image, (int(size[0] * scale_x), int(size[1] * scale_y)))


def fixed_resize_width(image, to_size_x):
    size_x, size_y = image.get_size()
    return resize(image, to_size_x/size_x)


def fixed_resize_height(image, to_size_y):
    size_x, size_y = image.get_size()
    return resize(image, to_size_y/size_y)


def fixed_resize_high_size(image, to_size):
    size_x, size_y = image.get_size()
    high_size = max(size_x, size_y)
    return resize(image, to_size/high_size)


def fixed_resize_lower_size(image, to_size):
    size_x, size_y = image.get_size()
    lower_size = min(size_x, size_y)
    return resize(image, to_size/lower_size)