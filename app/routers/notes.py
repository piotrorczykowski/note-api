from fastapi import APIRouter


router = APIRouter(prefix="/notes", tags=["Note"])


@router.get("", summary="Get all notes", response_description="List of notes")
def get_notes():
    return [{"id": 1, "content": "This is a note."}]


@router.post("", summary="Create a new note", response_description="The created note")
def create_note(note: dict):
    return {"id": 2, "content": note.get("content", "")}


@router.put(
    "/{note_id}", summary="Update a note", response_description="The updated note"
)
def update_note(note_id: int, note: dict):
    return {"id": note_id, "content": note.get("content", "")}


@router.delete(
    "/{note_id}", summary="Delete a note", response_description="Deletion status"
)
def delete_note(note_id: int):
    return {"status": "deleted", "id": note_id}
