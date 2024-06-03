import datetime
from .database import Base
from sqlalchemy import String, ForeignKey, Date, Float, Date, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import Enum


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(30), unique=True)
    password_hash: Mapped[str] = mapped_column(String())
    companies: Mapped[list["Company"]] = relationship(
        "Company", cascade="all,delete", back_populates="owner"
    )
    employees: Mapped[list["Employee"]] = relationship(
        "Employee", cascade="all,delete", back_populates="owner"
    )
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        "RefreshToken", cascade="all,delete", back_populates="user"
    )


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(primary_key=1)
    token_hash: Mapped[str] = mapped_column(String())
    expires: Mapped[datetime.datetime] = mapped_column(DateTime())
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="refresh_tokens")

    @classmethod
    def delete_expired_tokens(cls, db):
        db.query(cls).filter(datetime.datetime.now() > cls.expires).delete()
        db.commit()


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String())
    inn: Mapped[str] = mapped_column(String(10))
    kpp: Mapped[str] = mapped_column(String(9))
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    owner: Mapped["User"] = relationship("User", back_populates="companies")
    departments: Mapped[list["Department"]] = relationship(
        "Department", cascade="all,delete", back_populates="company"
    )


class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String())
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    company: Mapped["Company"] = relationship("Company", back_populates="departments")


class EmployeeGender(Enum):
    male = 1
    female = 2


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String())
    gender: Mapped[EmployeeGender] = mapped_column(SQLEnum(EmployeeGender))
    birthdate: Mapped[datetime.datetime] = mapped_column(DateTime())
    inn: Mapped[str] = mapped_column(String(12))
    snils: Mapped[str] = mapped_column(String(11))
    address: Mapped[str] = mapped_column(String())
    passport_number: Mapped[str] = mapped_column(String(10))
    passport_date: Mapped[str] = mapped_column(String())
    passport_issuer: Mapped[str] = mapped_column(String())
    actions: Mapped[list["Action"]] = relationship(
        "Action", cascade="all,delete", back_populates="employee"
    )
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    owner: Mapped["User"] = relationship("User", back_populates="employees")

    @property
    def current_position(self) -> str | None:
        if any(action.action_type == "dismissal" for action in self.actions):
            return None

        try:
            recruitment = [
                action for action in self.actions if action.action_type == "recruitment"
            ][0]
        except IndexError:
            return None

        position_transfers = [
            action
            for action in self.actions
            if action.action_type == "position_transfer"
        ]
        position_transfers = sorted(
            position_transfers, key=lambda transfer: transfer.date
        )
        return (
            position_transfers[-1].new_position
            if position_transfers
            else recruitment.position
        )

    @property
    def current_department(self) -> Department | None:
        if any(action.action_type == "dismissal" for action in self.actions):
            return None

        try:
            recruitment = [
                action for action in self.actions if action.action_type == "recruitment"
            ][0]
        except IndexError:
            return None

        department_transfers = [
            action
            for action in self.actions
            if action.action_type == "department_transfer"
        ]
        department_transfers = sorted(
            department_transfers, key=lambda transfer: transfer.date
        )
        return (
            department_transfers[-1].new_department
            if department_transfers
            else recruitment.department
        )

    @property
    def current_salary(self) -> float | None:
        if any(action.action_type == "dismissal" for action in self.actions):
            return None

        try:
            recruitment = [
                action for action in self.actions if action.action_type == "recruitment"
            ][0]
        except IndexError:
            return None

        salary_changes = [
            action for action in self.actions if action.action_type == "salary_change"
        ]
        salary_changes = sorted(salary_changes, key=lambda transfer: transfer.date)
        return salary_changes[-1].new_salary if salary_changes else recruitment.salary

    @property
    def current_company(self) -> Company:
        if not self.current_department:
            return None
        return self.current_department.company

    @property
    def last_copmany(self) -> Company:
        try:
            recruitment = [
                action for action in self.actions if action.action_type == "recruitment"
            ][0]
        except IndexError:
            return None

        department_transfers = [
            action
            for action in self.actions
            if action.action_type == "department_transfer"
        ]
        department_transfers = sorted(
            department_transfers, key=lambda transfer: transfer.date
        )
        return (
            department_transfers[-1].new_department.company
            if department_transfers
            else recruitment.department.company
        )


class Action(Base):
    __tablename__ = "actions"

    id: Mapped[int] = mapped_column(primary_key=True)
    action_type = mapped_column(String(32), nullable=False)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"))
    employee: Mapped["Employee"] = relationship("Employee", back_populates="actions")
    date: Mapped[datetime.date] = mapped_column(Date(), nullable=True)
    __mapper_args__ = {"polymorphic_on": action_type}


class RecruitmentAction(Action):
    __mapper_args__ = {"polymorphic_identity": "recruitment"}

    department_id: Mapped[int] = mapped_column(
        ForeignKey("departments.id"), nullable=True
    )
    department: Mapped["Department"] = relationship(foreign_keys=[department_id])
    position: Mapped[str] = mapped_column(String(), nullable=True)
    salary: Mapped[float] = mapped_column(Float(), nullable=True)


class PositionTransferAction(Action):
    __mapper_args__ = {"polymorphic_identity": "position_transfer"}

    new_position: Mapped[str] = mapped_column(String(), nullable=True)


class DepartmentTransferAction(Action):
    __mapper_args__ = {"polymorphic_identity": "department_transfer"}

    new_department_id: Mapped[int] = mapped_column(
        ForeignKey("departments.id"), nullable=True
    )
    new_department: Mapped["Department"] = relationship(
        foreign_keys=[new_department_id]
    )


class SalaryChangeAction(Action):
    __mapper_args__ = {"polymorphic_identity": "salary_change"}

    new_salary: Mapped[float] = mapped_column(Float(), nullable=True)


class DismissalAction(Action):
    __mapper_args__ = {"polymorphic_identity": "dismissal"}
