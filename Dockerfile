FROM python
WORKDIR /app/
COPY server.py /app/
COPY optimize /app/optimize
COPY requirements.txt /app/
RUN pip install -r requirements.txt
CMD ["python", "server.py"]