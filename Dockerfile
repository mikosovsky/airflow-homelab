FROM apache/airflow:latest
USER root
COPY requirements.txt /requirements.txt
COPY --chown=airflow:root airflow_provider_elevenlabs /opt/airflow/airflow_provider_elevenlabs
USER airflow
RUN pip install --no-cache-dir -r /requirements.txt \
	&& pip install /opt/airflow/airflow_provider_elevenlabs