from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from .database import Base


class Note(Base):
    __tablename__ = 'note'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    note = Column(String)
    note_file = Column(String)
    user_id = Column(Integer, ForeignKey('user.id'))

    owner = relationship("User", back_populates="notes")

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String)
    password = Column(String)

    notes = relationship("Note", back_populates="owner")