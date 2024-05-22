"""change actions

Revision ID: 3cda4289bcde
Revises: 0976f21b55f4
Create Date: 2024-05-22 01:57:50.333290

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "3cda4289bcde"
down_revision: Union[str, None] = "0976f21b55f4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("actions", sa.Column("date", sa.DATE(), nullable=True))

    actions = sa.table(
        "actions",
        sa.column("action_type", sa.VARCHAR(32)),
        sa.column("change_date", sa.DATE()),
        sa.column("recruitment_date", sa.DATE()),
        sa.column("end_date", sa.DATE()),
        sa.column("transfer_date", sa.DATE()),
        sa.column("start_date", sa.DATE()),
        sa.column("dismissal_date", sa.DATE()),
        sa.column("date", sa.DATE()),
    )

    op.execute(
        actions.update().values(
            date=sa.case(
                (actions.c.change_date != None, actions.c.change_date),
                (actions.c.recruitment_date != None, actions.c.recruitment_date),
                (actions.c.end_date != None, actions.c.end_date),
                (actions.c.transfer_date != None, actions.c.transfer_date),
                (actions.c.start_date != None, actions.c.start_date),
                (actions.c.dismissal_date != None, actions.c.dismissal_date),
                else_=None,
            )
        )
    )

    op.drop_column("actions", "change_date")
    op.drop_column("actions", "recruitment_date")
    op.drop_column("actions", "end_date")
    op.drop_column("actions", "transfer_date")
    op.drop_column("actions", "start_date")
    op.drop_column("actions", "dismissal_date")

    op.execute(
        actions.update()
        .where(actions.c.action_type == "dissmisal")
        .values(action_type="dismissal")
    )


def downgrade() -> None:
    op.add_column(
        "actions",
        sa.Column("dismissal_date", sa.DATE(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "actions",
        sa.Column("start_date", sa.DATE(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "actions",
        sa.Column("transfer_date", sa.DATE(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "actions", sa.Column("end_date", sa.DATE(), autoincrement=False, nullable=True)
    )
    op.add_column(
        "actions",
        sa.Column("recruitment_date", sa.DATE(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "actions",
        sa.Column("change_date", sa.DATE(), autoincrement=False, nullable=True),
    )

    actions = sa.table(
        "actions",
        sa.column("action_type", sa.String),
        sa.column("change_date", sa.DATE()),
        sa.column("recruitment_date", sa.DATE()),
        sa.column("end_date", sa.DATE()),
        sa.column("transfer_date", sa.DATE()),
        sa.column("start_date", sa.DATE()),
        sa.column("dismissal_date", sa.DATE()),
        sa.column("date", sa.DATE()),
    )

    op.execute(
        actions.update()
        .where(actions.c.action_type == "recruitment")
        .values(recruitment_date=actions.c.date)
    )
    op.execute(
        actions.update()
        .where(actions.c.action_type == "position_transfer")
        .values(transfer_date=actions.c.date)
    )
    op.execute(
        actions.update()
        .where(actions.c.action_type == "department_transfer")
        .values(transfer_date=actions.c.date)
    )
    op.execute(
        actions.update()
        .where(actions.c.action_type == "salary_change")
        .values(change_date=actions.c.date)
    )
    op.execute(
        actions.update()
        .where(actions.c.action_type == "dismissal")
        .values(dismissal_date=actions.c.date)
    )

    op.drop_column("events", "date")

    op.execute(
        actions.update()
        .where(actions.c.action_type == "dismissal")
        .values(action_type="dissmisal")
    )
