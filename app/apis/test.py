from sqlalchemy.orm import Session
from app.crud import crud_test

def test_index(db:Session):
    # uids = [10000, 10001, 10002]
    # something = crud_test.get_item(db, uids)
    something = crud_test.friends_list_invite(db, 11405)
    # something = crud_user_data.save(db, 10180, 'equipment', 'ddd')
    return something