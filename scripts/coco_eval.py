import json
import os
#import pickle
import random
from typing import List, Tuple, Dict

# import torch
# import torch.utils.data.dataset
# from PIL import Image, ImageOps
from pycocotools.coco import COCO
from pycocotools.cocoeval import COCOeval
# from torch import Tensor
# from torchvision.datasets import CocoDetection
# from tqdm import tqdm

# from bbox import BBox
# from dataset.base import Base
from io import StringIO
import sys


class COCO2017():
    CATEGORY_TO_LABEL_DICT = {
        'background': 0, 'person': 1, 'bicycle': 2, 'car': 3, 'motorcycle': 4,
        'airplane': 5, 'bus': 6, 'train': 7, 'truck': 8, 'boat': 9,
        'traffic light': 10, 'fire hydrant': 11, 'street sign': 12, 'stop sign': 13, 'parking meter': 14,
        'bench': 15, 'bird': 16, 'cat': 17, 'dog': 18, 'horse': 19,
        'sheep': 20, 'cow': 21, 'elephant': 22, 'bear': 23, 'zebra': 24,
        'giraffe': 25, 'hat': 26, 'backpack': 27, 'umbrella': 28, 'shoe': 29,
        'eye glasses': 30, 'handbag': 31, 'tie': 32, 'suitcase': 33, 'frisbee': 34,
        'skis': 35, 'snowboard': 36, 'sports ball': 37, 'kite': 38, 'baseball bat': 39,
        'baseball glove': 40, 'skateboard': 41, 'surfboard': 42, 'tennis racket': 43, 'bottle': 44,
        'plate': 45, 'wine glass': 46, 'cup': 47, 'fork': 48, 'knife': 49,
        'spoon': 50, 'bowl': 51, 'banana': 52, 'apple': 53, 'sandwich': 54,
        'orange': 55, 'broccoli': 56, 'carrot': 57, 'hot dog': 58, 'pizza': 59,
        'donut': 60, 'cake': 61, 'chair': 62, 'couch': 63, 'potted plant': 64,
        'bed': 65, 'mirror': 66, 'dining table': 67, 'window': 68, 'desk': 69,
        'toilet': 70, 'door': 71, 'tv': 72, 'laptop': 73, 'mouse': 74,
        'remote': 75, 'keyboard': 76, 'cell phone': 77, 'microwave': 78, 'oven': 79,
        'toaster': 80, 'sink': 81, 'refrigerator': 82, 'blender': 83, 'book': 84,
        'clock': 85, 'vase': 86, 'scissors': 87, 'teddy bear': 88, 'hair drier': 89,
        'toothbrush': 90, 'hair brush': 91
    }

    LABEL_TO_CATEGORY_DICT = {v: k for k, v in CATEGORY_TO_LABEL_DICT.items()}

    def __init__(self, path_to_data_dir, mode, image_min_side, image_max_side):

        path_to_jpeg_images_dir = os.path.join(path_to_coco_dir, 'val2017')
        path_to_annotation = os.path.join(path_to_annotations_dir, 'instances_val2017.json')

    def evaluate(self, path_to_results_dir: str, image_ids: List[str], bboxes: List[List[float]], classes: List[int], probs: List[float]) -> Tuple[float, str]:
        self._write_results(path_to_results_dir, image_ids, bboxes, classes, probs)

        annType = 'bbox'
        path_to_coco_dir = os.path.join(self._path_to_data_dir, 'COCO')
        path_to_annotations_dir = os.path.join(path_to_coco_dir, 'annotations')
        path_to_annotation = os.path.join(path_to_annotations_dir, 'instances_val2017.json')

        cocoGt = COCO(path_to_annotation)
        cocoDt = cocoGt.loadRes(os.path.join(path_to_results_dir, 'results.json'))

        cocoEval = COCOeval(cocoGt, cocoDt, annType)
        cocoEval.evaluate()
        cocoEval.accumulate()

        original_stdout = sys.stdout
        string_stdout = StringIO()
        sys.stdout = string_stdout
        cocoEval.summarize()
        sys.stdout = original_stdout

        mean_ap = cocoEval.stats[0].item()  # stats[0] records AP@[0.5:0.95]
        detail = string_stdout.getvalue()

        return mean_ap, detail

    def _write_results(self, path_to_results_dir: str, image_ids: List[str], bboxes: List[List[float]], classes: List[int], probs: List[float]):
        results = []
        for image_id, bbox, cls, prob in zip(image_ids, bboxes, classes, probs):
            results.append(
                {
                    'image_id': int(image_id),  # COCO evaluation requires `image_id` to be type `int`
                    'category_id': cls,
                    'bbox': [   # format [left, top, width, height] is expected
                        bbox[0],
                        bbox[1],
                        bbox[2] - bbox[0],
                        bbox[3] - bbox[1]
                    ],
                    'score': prob
                }
            )

        with open(os.path.join(path_to_results_dir, 'results.json'), 'w') as f:
            json.dump(results, f)

