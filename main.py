import os
import datetime
import json
import logging
from typing import Any
from dataclasses import dataclass, asdict

from bottle import Bottle, request, template, HTTPResponse, static_file
from playhouse.shortcuts import model_to_dict
import peewee

logger = logging.getLogger(__name__)

#### Database

DATABASE_FILE = "database/enquate_app.db"
db = peewee.SqliteDatabase(DATABASE_FILE)


class Base(peewee.Model):
    class Meta:
        database = db


class Opinion(Base):
    create_at = peewee.DateTimeField(default=datetime.datetime.now)
    topic = peewee.CharField()
    content = peewee.CharField()


def create_table():
    if not os.path.exists(DATABASE_FILE):
        db.create_tables([Opinion])
        logger.info("Create new tables.")


#### Bottle

app = Bottle()
app.config["autojson"] = True


@dataclass
class SchemaEquate:
    topic: str
    content: str

    @classmethod
    def load_from_dict(cls, data: dict[str, Any]):
        return cls(
            topic=data.get("topic", "-"),
            content=data.get("content", "-"),
        )


@app.route("/")
def index():
    return template("index")


@app.route("/static/<filename:path>")
def send_static(filename):
    return static_file(filename, root="static")


@app.route("/enquates", method="POST")
def post_enquate():
    data = SchemaEquate.load_from_dict(
        {
            "topic": request.forms.topic,
            "content": request.forms.content,
        }
    )
    Opinion.create(topic=data.topic, content=data.content)

    return "<p>回答が送信されました。</p>"


# def post_enquate_json():
#     data = SchemaEquate.load_from_dict(request.json)
#     Opinion.create(topic=data.topic, content=data.content)

#     header = {
#         "Content-Type": "application/json",
#         "Access-Control-Allow-Origin": "*",
#         "Access-Control-Allow-Headers": "Origin, X-Requested-With, Content-Type, Accept, Authorization",
#     }
#     ret = HTTPResponse(
#         status=200,
#         body=json.dumps(asdict(data)),
#         headers=header,
#     )
#     return ret


# @app.route("/enquates", method="GET")
# def get_enquates_json():
#     def to_jsonable_dict(data) -> dict[str, Any]:
#         converted = model_to_dict(data)
#         for key, value in converted.items():
#             if isinstance(value, datetime.datetime):
#                 converted[key] = value.isoformat()
#         return converted

#     records = Opinion.select().order_by(Opinion.create_at.desc())
#     jsonable_records = list()
#     for record in records:
#         jsonable_records.append(to_jsonable_dict(record))

#     header = {
#         "Content-Type": "application/json",
#         "Access-Control-Allow-Origin": "*",
#         "Access-Control-Allow-Headers": "Origin, X-Requested-With, Content-Type, Accept, Authorization",
#     }
#     ret = HTTPResponse(
#         status=200,
#         body=json.dumps(jsonable_records),
#         headers=header,
#     )
#     return ret


@app.route("/result", method="GET")
def get_result():
    def to_htmlable_dict(data) -> dict[str, Any]:
        converted = model_to_dict(data)
        for key, value in converted.items():
            if isinstance(value, datetime.datetime):
                converted[key] = value.isoformat()
            if isinstance(value, str):
                converted[key] = "<br>".join(value.splitlines())

        return converted

    records = Opinion.select().order_by(Opinion.create_at.desc())
    htmlable_records = list()
    for record in records:
        htmlable_records.append(to_htmlable_dict(record))

    context_data = {"data": htmlable_records}
    logger.debug(htmlable_records)

    return template("list", **context_data)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    create_table()
    app.run(host="0.0.0.0", port=8080, reloader=True)
