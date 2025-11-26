from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, Text, Date, Time, Numeric, ForeignKey

Base = declarative_base()

class AppUser(Base):
    __tablename__ = "app_user"
    user_id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True)
    given_name = Column(String(100))
    surname = Column(String(100))
    city = Column(String(100))
    phone_number = Column(String(30))
    profile_description = Column(Text)
    password = Column(String(255))

    caregiver = relationship("Caregiver", back_populates="user", uselist=False)
    member = relationship("Member", back_populates="user", uselist=False)


class Caregiver(Base):
    __tablename__ = "caregiver"
    caregiver_user_id = Column(Integer, ForeignKey("app_user.user_id"), primary_key=True)
    gender = Column(String(10))
    caregiving_type = Column(String(20))
    hourly_rate = Column(Numeric(6,2))
    
    photo_url = Column(Text)
    photo_thumb_url = Column(Text)
    photo_filename = Column(Text)
    photo_content_type = Column(Text)
    photo_size_bytes = Column(Integer)
    photo_uploaded_at = Column(Date)

    user = relationship("AppUser", back_populates="caregiver")


class Member(Base):
    __tablename__ = "member"
    member_user_id = Column(Integer, ForeignKey("app_user.user_id"), primary_key=True)
    house_rules = Column(Text)
    dependent_description = Column(Text)

    user = relationship("AppUser", back_populates="member")
    address = relationship("Address", back_populates="member", uselist=False)


class Address(Base):
    __tablename__ = "address"
    address_id = Column(Integer, primary_key=True)
    member_user_id = Column(Integer, ForeignKey("member.member_user_id"))
    house_number = Column(String(30))
    street = Column(String(200))
    town = Column(String(100))

    member = relationship("Member", back_populates="address")


class Job(Base):
    __tablename__ = "job"
    job_id = Column(Integer, primary_key=True)
    member_user_id = Column(Integer, ForeignKey("member.member_user_id"))
    required_caregiving_type = Column(String(20))
    other_requirements = Column(Text)
    date_posted = Column(Date)


class JobApplication(Base):
    __tablename__ = "job_application"
    caregiver_user_id = Column(Integer, ForeignKey("caregiver.caregiver_user_id"), primary_key=True)
    job_id = Column(Integer, ForeignKey("job.job_id"), primary_key=True)
    date_applied = Column(Date)


class Appointment(Base):
    __tablename__ = "appointment"
    appointment_id = Column(Integer, primary_key=True)
    caregiver_user_id = Column(Integer, ForeignKey("caregiver.caregiver_user_id"))
    member_user_id = Column(Integer, ForeignKey("member.member_user_id"))
    appointment_date = Column(Date)
    appointment_time = Column(Time)
    work_hours = Column(Numeric(5,2))
    status = Column(String(20))

