import datetime
from xml.dom.minidom import Document
from .database import Base
from sqlalchemy import String, ForeignKey, Date, Float, Date, Interval
from sqlalchemy.orm import Mapped, mapped_column, relationship


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(30), unique=True)
    password_hash: Mapped[str] = mapped_column(String())
    companies: Mapped[list["Company"]] = relationship(
        "Company", cascade="all,delete", back_populates="owner"
    )


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String())
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    owner: Mapped["User"] = relationship("User", back_populates="companies")
    departments: Mapped[list["Department"]] = relationship(
        "Department", cascade="all,delete", back_populates="company"
    )
    employees: Mapped[list["Employee"]] = relationship(
        "Employee", cascade="all,delete", back_populates="company"
    )


class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String())
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    company: Mapped["Company"] = relationship("Company", back_populates="departments")


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String())
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    company: Mapped["Company"] = relationship("Company", back_populates="employees")
    actions: Mapped[list["Action"]] = relationship(
        "Action", cascade="all,delete", back_populates="employee"
    )

    @property
    def current_position(self) -> str:
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
            position_transfers, key=lambda transfer: transfer.transfer_date
        )
        return (
            position_transfers[-1].new_position
            if position_transfers
            else recruitment.position
        )

    @property
    def current_department(self) -> Department:
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
            department_transfers, key=lambda transfer: transfer.transfer_date
        )
        return (
            department_transfers[-1].new_department
            if department_transfers
            else recruitment.department
        )

    @property
    def current_salary(self) -> float:
        try:
            recruitment = [
                action for action in self.actions if action.action_type == "recruitment"
            ][0]
        except IndexError:
            return None

        salary_changes = [
            action for action in self.actions if action.action_type == "salary_change"
        ]
        salary_changes = sorted(
            salary_changes, key=lambda transfer: transfer.change_date
        )
        return salary_changes[-1].new_salary if salary_changes else recruitment.salary


class Action(Base):
    __tablename__ = "actions"

    id: Mapped[int] = mapped_column(primary_key=True)
    action_type = mapped_column(String(32), nullable=False)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"))
    employee: Mapped["Employee"] = relationship("Employee", back_populates="actions")
    __mapper_args__ = {"polymorphic_on": action_type}


class RecruitmentAction(Action):
    __mapper_args__ = {"polymorphic_identity": "recruitment"}

    department_id: Mapped[int] = mapped_column(
        ForeignKey("departments.id"), nullable=True
    )
    department: Mapped["Department"] = relationship(foreign_keys=[department_id])
    recruitment_date: Mapped[datetime.date] = mapped_column(Date(), nullable=True)
    position: Mapped[str] = mapped_column(String(), nullable=True)
    salary: Mapped[float] = mapped_column(Float(), nullable=True)


class PositionTransferAction(Action):
    __mapper_args__ = {"polymorphic_identity": "position_transfer"}

    transfer_date: Mapped[datetime.date] = mapped_column(
        Date(), use_existing_column=True, nullable=True
    )
    new_position: Mapped[str] = mapped_column(String(), nullable=True)


class DepartmentTransferAction(Action):
    __mapper_args__ = {"polymorphic_identity": "department_transfer"}

    transfer_date: Mapped[datetime.date] = mapped_column(
        Date(), use_existing_column=True, nullable=True
    )
    new_department_id: Mapped[int] = mapped_column(
        ForeignKey("departments.id"), nullable=True
    )
    new_department: Mapped["Department"] = relationship(
        foreign_keys=[new_department_id]
    )


class SalaryChangeAction(Action):
    __mapper_args__ = {"polymorphic_identity": "salary_change"}

    change_date: Mapped[datetime.date] = mapped_column(Date(), nullable=True)
    new_salary: Mapped[float] = mapped_column(Float(), nullable=True)


class VacationAction(Action):
    __mapper_args__ = {"polymorphic_identity": "vacation"}

    start_date: Mapped[datetime.date] = mapped_column(
        Date(), use_existing_column=True, nullable=True
    )
    end_date: Mapped[datetime.date] = mapped_column(
        Date(), use_existing_column=True, nullable=True
    )


class SickLeaveAction(Action):
    __mapper_args__ = {"polymorphic_identity": "sick_leave"}

    start_date: Mapped[datetime.date] = mapped_column(
        Date(), use_existing_column=True, nullable=True
    )
    end_date: Mapped[datetime.date] = mapped_column(
        Date(), use_existing_column=True, nullable=True
    )


class DissmisalAction(Action):
    __mapper_args__ = {"polymorphic_identity": "dissmisal"}

    dismissal_date: Mapped[datetime.date] = mapped_column(Date(), nullable=True)
