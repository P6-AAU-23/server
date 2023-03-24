from CornerProvider import CornerProvider
from typing import Dict, Tuple
from helper import distance
import numpy as np
import cv2
from enum import Enum


class Pipeline:
    def __init__(self):
        self.corner_provider = CornerProvider("Corner Selection Preview")

    def process(self, image):
        self.corner_provider.update(image)
        corners = self.corner_provider.get_corners()
        whiteboard = quadrilateral_to_rectangle(image, corners)
        whiteboard = remove_foreground(whiteboard) 
        whiteboard = idealize_colors(whiteboard, Idealize_colors_mode.MASKING)
        whiteboard = inpaint_missing(whiteboard)
        return whiteboard


def quadrilateral_to_rectangle(
    image: np.ndarray, corners: Dict[str, Tuple[int, int]]
) -> np.ndarray:
    """
    Warps a quadrilateral region in the input image into a rectangular shape using a perspective transformation.

    :param image: A numpy array representing the input image.
    :param corners: A dictionary containing 4 corner points defining the quadrilateral region in the input image.
                    The keys should be 'upper_left', 'upper_right', 'lower_right', 'lower_left', and the values are
                    tuples containing the x and y coordinates (integers) of each corner point.
    :return: A numpy array representing the output image with the quadrilateral region warped into a rectangular shape.
    """
    width_upper = distance(corners["upper_left"], corners["upper_right"])
    width_lower = distance(corners["lower_left"], corners["lower_right"])
    max_width = int(max(width_upper, width_lower))
    height_left = distance(corners["upper_left"], corners["lower_left"])
    height_right = distance(corners["upper_right"], corners["lower_right"])
    max_height = int(max(height_left, height_right))
    target_corners = np.array(
        [(0, 0), (max_width, 0), (max_width, max_height), (0, max_height)],
        dtype=np.float32,
    )
    quad_to_rect_transform = cv2.getPerspectiveTransform(np.float32(list(corners.values())), target_corners)  # type: ignore
    out = cv2.warpPerspective(image, quad_to_rect_transform, (max_width, max_height))  # type: ignore
    return out


def remove_foreground(image: np.ndarray) -> np.ndarray:
    return image

class Idealize_colors_mode(Enum):
    MASKING = 1
    ASSIGN_EXTREME = 2


def idealize_colors(image: np.ndarray, mode: Idealize_colors_mode) -> np.ndarray:
    if mode == Idealize_colors_mode.MASKING:
        return  idealize_colors_masking(image)
    if mode == Idealize_colors_mode.ASSIGN_EXTREME:
        return  idealize_colors_assign_extreme(image)
    else: 
        return image


def idealize_colors_masking(image: np.ndarray) -> np.ndarray:
    mask = binarize(image)
    masked_image = apply_mask(image, mask)
    return masked_image


def idealize_colors_assign_extreme(image: np.ndarray) -> np.ndarray:
    threshold = 128
    max_val = 255
    # Split the image into B, G, and R channels
    b, g, r = cv2.split(image)  # type: ignore
    # Apply the threshold to each channel
    _, b = cv2.threshold(b, threshold, max_val, cv2.THRESH_BINARY)  # type: ignore
    _, g = cv2.threshold(g, threshold, max_val, cv2.THRESH_BINARY)  # type: ignore
    _, r = cv2.threshold(r, threshold, max_val, cv2.THRESH_BINARY)  # type: ignore
    # Merge the thresholded channels back into a single image
    recolored_image = cv2.merge((b, g, r))  # type: ignore
    return recolored_image


def apply_mask(image: np.ndarray, mask: np.ndarray) -> np.ndarray:
    masked_image = cv2.bitwise_and(image, image, mask=mask)  # type: ignore
    masked_image[mask==0] = 255  # make the masked area white
    return masked_image


def binarize(image: np.ndarray) -> np.ndarray:
    image_grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # type: ignore  
    binary_image = cv2.adaptiveThreshold(image_grey, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 21, 4)  # type: ignore
    binary_image = cv2.medianBlur(binary_image, 3)  # type: ignore
    binary_image = cv2.bitwise_not(binary_image) # type: ignore
    return binary_image


def increase_hue(image: np.ndarray, amount: float) -> np.ndarray:
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGRA2HSV)  # type: ignore
    # Increase the saturation by amount%
    hsv_image[..., 1] = hsv_image[..., 1] * amount
    output_image = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGRA)  # type: ignore
    return output_image


def inpaint_missing(image: np.ndarray) -> np.ndarray:
    return image
