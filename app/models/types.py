from enum import IntEnum

class ArtifactType(IntEnum):
    DATASET = 1
    MODEL = 2
    PRODUCT = 3


class GithubRepositoryType(IntEnum):
    SOFTWARE = 1
    HFML = 2
    OTHERML = 3
    HFVISUAL = 4