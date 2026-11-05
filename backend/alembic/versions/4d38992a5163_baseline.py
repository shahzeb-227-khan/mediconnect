"""baseline

Revision ID: 4d38992a5163
Revises: 
Create Date: 2026-07-07 16:32:53.395290

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from src.utils.database import Base
from src.cities.models import City
from src.specializations.models import Specialization
from src.hospitals.models import Hospital
from src.doctors.models import Doctor
from src.doctor_hospitals.models import DoctorHospital
from src.patients.models import Patient
from src.appointments.models import Appointment
from src.reviews.models import Review


# revision identifiers, used by Alembic.
revision: str = '4d38992a5163'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # The original baseline was empty because the application created tables
    # at startup. Keep the migration chain usable for new databases.
    Base.metadata.create_all(bind=op.get_bind())


def downgrade() -> None:
    """Downgrade schema."""
    Base.metadata.drop_all(bind=op.get_bind())
