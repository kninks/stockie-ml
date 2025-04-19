from enum import Enum


class MeasurementMetric(str, Enum):
    total_predict_time = "predict"
    inference_time = "infer"
    load_time = "load"


class MeasurementTag(str, Enum):
    env = "env"
    ticker = "ticker"
    status = "status"
    source = "source"
    file_type = "file"


class MeasurementValue(str, Enum):
    local = "local"
    prod = "prod"

    success = "success"
    fail = "fail"

    # load: cache / download
    download = "download"
    cache = "cache"

    model = "model"
    scaler = "scaler"
