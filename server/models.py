from datetime import datetime
from .database import Base
from sqlalchemy import DateTime, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(30), unique=True)
    password_hash: Mapped[str] = mapped_column(String())
    companies: Mapped[list["Company"]] = relationship("Company", cascade="all,delete", back_populates="owner")


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String())
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    owner: Mapped["User"] = relationship("User", back_populates="companies")
    departments: Mapped[list["Department"]] = relationship("Department", cascade="all,delete", back_populates="company")


class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String())
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    company: Mapped["Company"] = relationship("Company", back_populates="departments")
    employees: Mapped[list["Employee"]] = relationship("Employee", cascade="all,delete", back_populates="department")


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String())
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"))
    department: Mapped["Department"] = relationship("Department", back_populates="employees")
    positions: Mapped[list["Position"]] = relationship("Position", cascade="all,delete", back_populates="employee")


class Position(Base):
    __tablename__ = "positions"

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"))
    employee: Mapped["Employee"] = relationship("Employee", back_populates="positions")
    name: Mapped[str] = mapped_column(String())
    start_date: Mapped[datetime] = mapped_column(DateTime())
    end_date: Mapped[datetime] = mapped_column(DateTime(), nullable=True)
