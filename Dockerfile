FROM python:3.6-slim
RUN mkdir /code  
WORKDIR /code  
ADD ./*.py /code/  
RUN pip install -r requirements.txt  
RUN mkdir /var/archivos_ioc/
CMD ["python", "/code/bot.py"]`
