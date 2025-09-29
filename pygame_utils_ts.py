import pygame
import math


def draw_gradient_rect(surface, rect, outer_color, inner_color):
    x, y, w, h = rect
    gradient_surf = pygame.Surface((w, h), pygame.SRCALPHA)

    center_x, center_y = w // 2, h // 2
    max_radius = math.hypot(center_x, center_y)

    for radius in range(int(max_radius), 0, -1):
        t = (radius / max_radius) * 0.6
        r = int(inner_color[0] * (1 - t) + outer_color[0] * t)
        g = int(inner_color[1] * (1 - t) + outer_color[1] * t)
        b = int(inner_color[2] * (1 - t) + outer_color[2] * t)
        alpha = 255 - int(200 * t)

        pygame.draw.circle(
            gradient_surf,
            (r, g, b),
            (center_x, center_y),
            radius
        )

    surface.blit(gradient_surf, (x, y))

