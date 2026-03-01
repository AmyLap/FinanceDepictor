from .dashboard import render as render_dashboard
from .upload_statements import render as render_upload_statements
from .monthly_analysis import render as render_monthly_analysis
from .categories import render as render_categories
from .year_analysis import render as render_year_analysis

PAGE_NAMES = [
    "Dashboard",
    "Upload Statements",
    "Monthly Analysis",
    "Categories",
    "Year Analysis",
]

PAGE_RENDERERS = {
    "Dashboard": render_dashboard,
    "Upload Statements": render_upload_statements,
    "Monthly Analysis": render_monthly_analysis,
    "Categories": render_categories,
    "Year Analysis": render_year_analysis,
}
