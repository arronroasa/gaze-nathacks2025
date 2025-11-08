FROM python:3.12-slim

WORKDIR /prog

COPY . /prog

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Write all python files to be ran here
# Each CMD call is like a bash execution like: "python test.py" should be ["python", "test.py"]
CMD ["python", "test.py"]