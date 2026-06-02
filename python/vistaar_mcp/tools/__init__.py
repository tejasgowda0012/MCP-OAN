"""Vistaar agent tool implementations (MCP server)."""

from vistaar_mcp.tools.scheme_info import get_scheme_info
from vistaar_mcp.tools.pmkisan_scheme_status import (
    initiate_pm_kisan_status_check,
    check_pm_kisan_status_with_otp,
)
from vistaar_mcp.tools.pmfby_scheme_status import (
    initiate_pmfby_status_check,
    check_pmfby_status_with_otp,
)
from vistaar_mcp.tools.shc_scheme_status import check_shc_status
from vistaar_mcp.tools.pmkisan_grievance import (
    pmkisan_grievance_send_otp,
    pmkisan_submit_grievance,
    pmkisan_grievance_status,
)
from vistaar_mcp.tools.smam_scheme_status import check_smam_scheme_status
from vistaar_mcp.tools.pmfby_grievance import (
    initiate_pmfby_grievance_otp,
    check_pmfby_grievance_otp,
    pmfby_grievance_status,
    pmfby_submit_grievance,
)
from vistaar_mcp.tools.terms import search_terms
from vistaar_mcp.tools.search import (
    search_documents,
    search_videos,
    search_pests_diseases,
)
from vistaar_mcp.tools.weather import weather_forecast
from vistaar_mcp.tools.mandi import get_mandi_prices
from vistaar_mcp.tools.commodity import search_commodity
from vistaar_mcp.tools.maps import reverse_geocode, forward_geocode
from vistaar_mcp.tools.gfr import (
    gfr_get_crop_registries,
    gfr_get_recommendations,
)
from vistaar_mcp.tools.sathi_seed import (
    get_sathi_crop_groups,
    list_sathi_crops_in_group,
    search_sathi_seed_availability,
)
from vistaar_mcp.tools.npss import analyze_crop_image

__all__ = [
    "get_scheme_info",
    "initiate_pm_kisan_status_check",
    "check_pm_kisan_status_with_otp",
    "initiate_pmfby_status_check",
    "check_pmfby_status_with_otp",
    "check_shc_status",
    "pmkisan_grievance_send_otp",
    "check_smam_scheme_status",
    "pmkisan_submit_grievance",
    "pmkisan_grievance_status",
    "initiate_pmfby_grievance_otp",
    "check_pmfby_grievance_otp",
    "pmfby_grievance_status",
    "pmfby_submit_grievance",
    "search_terms",
    "search_documents",
    "search_videos",
    "search_pests_diseases",
    "weather_forecast",
    "get_mandi_prices",
    "search_commodity",
    "forward_geocode",
    "reverse_geocode",
    "gfr_get_crop_registries",
    "gfr_get_recommendations",
    "get_sathi_crop_groups",
    "list_sathi_crops_in_group",
    "search_sathi_seed_availability",
    "analyze_crop_image",
]