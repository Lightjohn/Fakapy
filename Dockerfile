FROM python:3.8
ADD requirements.txt /
RUN pip install -r requirements.txt

ADD *.py /
ADD fakapy/ /fakapy/

CMD ["python3", "quick test2.py"]