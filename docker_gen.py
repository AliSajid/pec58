"""
File to generate a bunch of Dockerfiles.
"""
from os import path, mkdir

lower_bounds = list(range(0, 10000000, 625000))
upper_bounds = list(range(625000, 10000001, 625000))
bounds = list(zip(lower_bounds, upper_bounds))
template = """
FROM continuumio/miniconda3

WORKDIR /app

RUN apt-get update

RUN apt-get install sqlite3

RUN git clone https://github.com/AliSajid/pec58.git

RUN pip install -r pec58/requirements.txt

CMD ["python", "/app/pec58/main.py", "-s {}", "-e {}"]
"""

for idx, pair in enumerate(bounds):
    dirname = path.join("build", "build{:0>2}".format(idx))
    if not path.isdir(dirname):
        mkdir(dirname)
    with open(path.join(dirname, "Dockerfile"), 'w') as f:
        f.write(template.format(pair[0], pair[1]))