from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.session import Base
from app.models.entities import Interaction, Track, User
from app.recommendations.engine import Recommender


def test_recommender_prefers_liked_genre():
    engine = create_engine("sqlite:///:memory:")
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = Session()

    user = User(username="alice")
    t1 = Track(provider="spotify", provider_track_id="1", title="A", artist="AA", genre="pop", duration_sec=200)
    t2 = Track(provider="spotify", provider_track_id="2", title="B", artist="BB", genre="rock", duration_sec=210)
    t3 = Track(provider="spotify", provider_track_id="3", title="C", artist="CC", genre="pop", duration_sec=220)

    db.add_all([user, t1, t2, t3])
    db.flush()
    db.add(Interaction(user_id=user.id, track_id=t1.id, event_type="like", value=1.0))
    db.commit()

    recs = Recommender().recommend_for_user(db, "alice", limit=2)
    assert recs
    assert recs[0].genre == "pop"
