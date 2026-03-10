from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, Text, Date, Time, Numeric, ForeignKey

Base = declarative_base()


class AppUser(Base):
    __tablename__ = "app_user"

    user_id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    given_name = Column(String(100))
    surname = Column(String(100))
    city = Column(String(100))
    phone_number = Column(String(30))
    profile_description = Column(Text)
    password = Column(String(255))

    caregiver = relationship("Caregiver", back_populates="user", uselist=False)
    member = relationship("Member", back_populates="user", uselist=False)

    def __repr__(self):
        return f"<AppUser id={self.user_id} email={self.email!r}>"


class Caregiver(Base):
    __tablename__ = "caregiver"

    caregiver_user_id = Column(Integer, ForeignKey("app_user.user_id"), primary_key=True)
    gender = Column(String(10))
    caregiving_type = Column(String(20))
    hourly_rate = Column(Integer)  # stored as rounded KZT integer e.g. 4500

    user = relationship("AppUser", back_populates="caregiver")
    appointments = relationship("Appointment", back_populates="caregiver")
    job_applications = relationship("JobApplication", back_populates="caregiver")

    def __repr__(self):
        return f"<Caregiver user_id={self.caregiver_user_id} type={self.caregiving_type!r}>"


class Member(Base):
    __tablename__ = "member"

    member_user_id = Column(Integer, ForeignKey("app_user.user_id"), primary_key=True)
    house_rules = Column(Text)
    dependent_description = Column(Text)

    user = relationship("AppUser", back_populates="member")
    address = relationship("Address", back_populates="member", uselist=False)
    jobs = relationship("Job", back_populates="member")
    appointments = relationship("Appointment", back_populates="member")

    def __repr__(self):
        return f"<Member user_id={self.member_user_id}>"


class Address(Base):
    __tablename__ = "address"

    address_id = Column(Integer, primary_key=True)
    member_user_id = Column(Integer, ForeignKey("member.member_user_id"), nullable=False)
    house_number = Column(String(30))
    street = Column(String(200))
    town = Column(String(100))

    member = relationship("Member", back_populates="address")

    def __repr__(self):
        return f"<Address id={self.address_id} {self.house_number} {self.street}, {self.town}>"


class Job(Base):
    __tablename__ = "job"

    job_id = Column(Integer, primary_key=True)
    member_user_id = Column(Integer, ForeignKey("member.member_user_id"), nullable=False)
    required_caregiving_type = Column(String(20))
    other_requirements = Column(Text)
    date_posted = Column(Date)

    member = relationship("Member", back_populates="jobs")
    applications = relationship("JobApplication", back_populates="job")

    def __repr__(self):
        return f"<Job id={self.job_id} type={self.required_caregiving_type!r}>"


class JobApplication(Base):
    __tablename__ = "job_application"

    caregiver_user_id = Column(Integer, ForeignKey("caregiver.caregiver_user_id"), primary_key=True)
    job_id = Column(Integer, ForeignKey("job.job_id"), primary_key=True)
    date_applied = Column(Date)

    caregiver = relationship("Caregiver", back_populates="job_applications")
    job = relationship("Job", back_populates="applications")

    def __repr__(self):
        return f"<JobApplication caregiver={self.caregiver_user_id} job={self.job_id}>"


class Appointment(Base):
    __tablename__ = "appointment"

    appointment_id = Column(Integer, primary_key=True)
    caregiver_user_id = Column(Integer, ForeignKey("caregiver.caregiver_user_id"), nullable=False)
    member_user_id = Column(Integer, ForeignKey("member.member_user_id"), nullable=False)
    appointment_date = Column(Date)
    appointment_time = Column(Time)
    work_hours = Column(Numeric(5, 2))
    status = Column(String(20))

    caregiver = relationship("Caregiver", back_populates="appointments")
    member = relationship("Member", back_populates="appointments")

    def __repr__(self):
        return f"<Appointment id={self.appointment_id} date={self.appointment_date} status={self.status!r}>"