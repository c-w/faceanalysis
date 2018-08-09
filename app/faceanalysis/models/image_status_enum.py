from enum import Enum


class ImageStatusEnum(Enum):
    finished_processing = 4
    processing = 3
    uploaded = 1
    face_vector_computed = 5
