import logging
import time
from typing import Optional

from google.auth import default
from google.cloud import monitoring_v3

from app.core.enums.measurement_enum import (
    MeasurementMetric,
    MeasurementTag,
    MeasurementValue,
)
from app.core.settings.config import get_config

logger = logging.getLogger(__name__)

try:
    credentials, project_id = default()
    client = monitoring_v3.MetricServiceClient(credentials=credentials)
    project_name = f"projects/{project_id}"
except Exception as e:
    logging.warning(f"[METRICS] Failed to init monitoring client: {e}")
    client = None
    project_name = None


def send_metric(
    metric: MeasurementMetric,
    value: str | float,
    tags: Optional[dict[MeasurementTag, MeasurementValue | str | float]] = None,
) -> None:
    if client is None or project_name is None:
        return

    try:
        series = monitoring_v3.TimeSeries()
        series.metric.type = f"custom.googleapis.com/ml/{metric.value}"
        series.resource.type = "global"

        env_str = get_config().ENVIRONMENT.lower()
        env = (
            MeasurementValue.prod.value
            if env_str == "prod"
            else MeasurementValue.local.value
        )
        series.metric.labels[MeasurementTag.env.value] = env

        if tags:
            for key, val in tags.items():
                if val in MeasurementValue:
                    val = val.value
                series.metric.labels[key.value] = val

        now = int(time.time())
        point = monitoring_v3.Point(
            {
                "interval": {"end_time": {"seconds": now}},
                "value": {"double_value": float(value)},
            }
        )
        series.points = [point]

        client.create_time_series(name=project_name, time_series=[series])
    except Exception as e:
        logging.error(f"[METRICS] Failed to send metric {metric}: {e}")
