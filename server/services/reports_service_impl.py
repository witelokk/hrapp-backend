from dataclasses import dataclass
from functools import cache
from io import BytesIO
import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from server.repo.companies_repository import CompaniesRepository
from server.repo.departments_repository import DepartmentsRepository
from server.repo.employees_repository import EmployeesRepository

from .reports_service import ReportsService, CompanyNotExistsError, ForbiddenError


TABLE_HEADER = ["ФИО", "Должность", "Зарплата"]


@cache
def find_font(font_name: str) -> str:
    font_paths = {
        "Linux": [
            "/usr/share/fonts/",
            "/usr/local/share/fonts/",
            os.path.expanduser("~/.fonts/"),
        ],
        "Darwin": [
            "/Library/Fonts/",
            "/System/Library/Fonts/",
            os.path.expanduser("~/Library/Fonts/"),
        ],
        "Windows": ["C:\\Windows\\Fonts\\"],
    }

    system = os.uname().sysname
    if system not in font_paths:
        raise ValueError(f"Unsupported OS: {system}")

    paths_to_search = font_paths[system]

    for path in paths_to_search:
        for root, dirs, files in os.walk(path):
            if font_name in files:
                return os.path.join(root, font_name)

    return None


@dataclass
class Employee:
    name: str
    position: str
    salary: str


@dataclass
class Department:
    name: str
    employees: list[Employee]


@dataclass
class CompanyReport:
    company_name: str
    departments: list[Department]


@dataclass
class CompanyReportGenerator:
    def __init__(
        self,
        companies_repository: CompaniesRepository,
        departments_repository: DepartmentsRepository,
        employees_repository: EmployeesRepository,
    ):
        self._companies_repository = companies_repository
        self._departments_repository = departments_repository
        self._employees_repository = employees_repository

    def _generate_employee_data(self, employee) -> Employee:
        return Employee(
            name=employee.name,
            position=employee.current_position,
            salary=employee.current_salary,
        )

    def _generate_employees_data(self, department_id: int) -> list[Employee]:
        employees = self._employees_repository.get_employees(department_id)
        return [self._generate_employee_data(employee) for employee in employees]

    def _generate_department_data(self, department) -> Department:
        return Department(
            name=department.name, employees=self._generate_employees_data(department.id)
        )

    def _generate_departments_data(self, company_id: int) -> list[Department]:
        departments = self._departments_repository.get_departments(company_id)
        return [
            self._generate_department_data(department) for department in departments
        ]

    def generate_report_data(self, company_id: int) -> CompanyReport:
        company = self._companies_repository.get_company(company_id)
        return CompanyReport(
            company_name=company.name,
            departments=self._generate_departments_data(company_id),
        )


class ReportsServiceImpl(ReportsService):
    def __init__(
        self,
        companies_repository: CompaniesRepository,
        departments_repository: DepartmentsRepository,
        employees_repository: EmployeesRepository,
    ):
        self._companies_repository = companies_repository
        self._departments_repository = departments_repository
        self._employees_repository = employees_repository

    def generate_report(self, user_id: int, company_id: int) -> bytes:
        company = self._companies_repository.get_company(company_id)

        if company is None:
            raise CompanyNotExistsError()

        if company.owner_id != user_id:
            raise ForbiddenError()

        report_data = CompanyReportGenerator(
            self._companies_repository,
            self._departments_repository,
            self._employees_repository,
        ).generate_report_data(company_id)
        return self._generate_report_pdf(report_data)

    def _generate_report_pdf(self, report_data: CompanyReport) -> bytes:
        pdfmetrics.registerFont(TTFont("DejaVuSans", find_font("DejaVuSans.ttf")))

        styles = getSampleStyleSheet()
        h1_style = ParagraphStyle(
            "H1",
            parent=styles["Normal"],
            fontName="DejaVuSans",
            fontSize=18,
            leading=18 * 1.4,
        )
        h2_style = ParagraphStyle(
            "H2",
            parent=styles["Normal"],
            fontName="DejaVuSans",
            fontSize=15,
            leading=15 * 1.4,
        )
        table_style = TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, 0), "DejaVuSans"),  # Header font
                ("FONTNAME", (0, 0), (-1, -1), "DejaVuSans"),  # Header font
                ("GRID", (0, 0), (-1, -1), 1, colors.black),  # Grid lines
            ]
        )

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = [Paragraph(report_data.company_name, h1_style)]

        for department in report_data.departments:
            elements.append(Paragraph(department.name, h2_style))
            elements.append(
                Table(
                    [TABLE_HEADER]
                    + [
                        [employee.name, employee.position, f"{employee.salary} ₽"]
                        for employee in department.employees
                    ],
                    style=table_style,
                )
            )
            elements.append(Paragraph("‎ ", h2_style))

        doc.build(elements)
        return buffer.getvalue()
