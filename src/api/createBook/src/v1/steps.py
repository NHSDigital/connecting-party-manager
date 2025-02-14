from http import HTTPStatus

from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from domain.core.epr.database import get_session, init_db
from domain.core.epr.models.base_models import Author, Book, Chapter
from domain.core.epr.models.request_models import CreateBookIncomingParams
from domain.response.validation_errors import (
    mark_json_decode_errors_as_inbound,
    mark_validation_errors_as_inbound,
)
from event.step_chain import StepChain


@mark_json_decode_errors_as_inbound
def parse_event_body(data, cache) -> dict:
    event = APIGatewayProxyEvent(data[StepChain.INIT])
    return event.json_body if event.body else {}


@mark_validation_errors_as_inbound
def parse_incoming_book(data, cache) -> CreateBookIncomingParams:
    json_body = data[parse_event_body]
    incoming_book = CreateBookIncomingParams(**json_body)
    return incoming_book


def create_book(data, cache) -> tuple[HTTPStatus, dict]:
    book_params: CreateBookIncomingParams = data[parse_incoming_book]
    init_db()
    try:
        session = get_session()

        author = session.query(Author).filter_by(name=book_params.author).first()
        if not author:
            author = Author(name=book_params.author)
            session.add(author)
            session.commit()

        book = Book(title=book_params.title, author_id=author.id)
        book.chapters = [Chapter(title=chapter) for chapter in book_params.chapters]

        session.add(book)
        session.commit()
        session.close()

        return HTTPStatus.CREATED, {"book_id": book.id}

    except Exception as e:
        return HTTPStatus.BAD_REQUEST, {
            "code": "RESOURCE_NOT_CREATED",
            "message": str(e),
        }


steps = [parse_event_body, parse_incoming_book, create_book]
