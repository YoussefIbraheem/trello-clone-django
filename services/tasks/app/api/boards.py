from app.models.board import Board
from app.schemas.board_schema import BoardCreate, BoardUpdate, BoardResponse
from app.services.board_service import (
    create_board,
    update_board,
    get_board_by_id,
    get_board_by_project,
    delete_board,
)
from flask import Blueprint, jsonify, request

boards_bp = Blueprint("boards", __name__, url_prefix="api/v1/boards/")


@boards_bp.route("/", methods=["GET"])
def boards_list():
    try:
        project_id = request.args.get("project_id")
        limit = request.args.get("limit")
        offset = request.args.get("offset")

        boards = get_board_by_project(project_id=project_id, limit=limit, offset=offset)

        data = [board.model_dump() for board in boards]

        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": f"{e}"}), 500


@boards_bp.route("/<int:board_id>", methods=["GET"])
def board_get():
    try:
        board_id = request.view_args["board_id"]
        board = get_board_by_id(board_id=board_id)

        return jsonify(board.model_dump()), 200
    except Exception as e:
        return jsonify({"error": f"{e}"}), 500


@boards_bp.route("/", methods=["POST"])
def board_create():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No Data Provided"}), 400

    try:
        board_data = BoardCreate(**data)
        created_board = create_board(board_data=board_data)
        return jsonify(created_board.model_dump())
    except Exception as e:
        return jsonify({"error": f"{e}"}), 500


@boards_bp.route("/<int:board_id>", methods=["PUT"])
def board_update(board_id):
    data = request.get_json()

    if not data:
        return jsonify({"error": "No Data Provided"}), 400

    try:
        board_data = BoardUpdate(**data)
        updated_board = update_board(board_id=board_id, board_data=board_data)
        return jsonify(updated_board.model_dump())
    except Exception as e:
        return jsonify({"error": f"{e}"}), 500


@boards_bp.route("/<int:board_id>", methods=["DELETE"])
def board_delete(board_id):
    try:
        success = delete_board(board_id=board_id)

        if not success:
            return jsonify({"error": "Board Not Found"}), 404

        return jsonify({"message": "Board Deleted Successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"{e}"}), 500
