# -*- coding: utf-8 -*-

try:
    # Python 2.7
    from collections import OrderedDict
except:
    # Python 2.6
    from gluon.contrib.simplejson.ordered_dict import OrderedDict

from datetime import timedelta

from gluon import current, Field, URL
from gluon.html import *
from gluon.storage import Storage
from gluon.validators import IS_NULL_OR, IS_NOT_EMPTY

from s3.s3fields import S3Represent
from s3.s3resource import S3FieldSelector
from s3.s3utils import S3DateTime, s3_auth_user_represent_name, s3_avatar_represent, s3_unicode
from s3.s3validators import IS_INT_AMOUNT, IS_LOCATION_SELECTOR2, IS_ONE_OF
from s3.s3widgets import S3LocationSelectorWidget2
from s3.s3forms import S3SQLCustomForm, S3SQLInlineComponent, S3SQLInlineComponentCheckbox

T = current.T
s3 = current.response.s3
settings = current.deployment_settings

"""
    Template settings for DRM Portal
"""

datetime_represent = lambda dt: S3DateTime.datetime_represent(dt, utc=True)

# =============================================================================
# System Settings
# -----------------------------------------------------------------------------
# Authorization Settings
settings.auth.registration_requires_approval = True
settings.auth.registration_requires_verification = False
settings.auth.registration_requests_organisation = True
settings.auth.registration_organisation_required = True
settings.auth.registration_requests_site = False

# Approval emails get sent to all admins
settings.mail.approver = "ADMIN"

settings.auth.registration_link_user_to = {"staff": T("Staff")}
settings.auth.registration_link_user_to_default = ["staff"]
settings.auth.registration_roles = {"organisation_id": ["USER"],
                                    }

# Terms of Service to be able to Register on the system
# uses <template>/views/tos.html
settings.auth.terms_of_service = True

settings.auth.show_utc_offset = False

settings.auth.show_link = False

settings.auth.record_approval = True
settings.auth.record_approval_required_for = ["org_organisation"]

# -----------------------------------------------------------------------------
# Security Policy
settings.security.policy = 6 # Realms
settings.security.map = True

# Owner Entity
settings.auth.person_realm_human_resource_site_then_org = False

def drmp_realm_entity(table, row):
    """
        Assign a Realm Entity to records
    """

    tablename = table._tablename

    if tablename == "cms_post":
        # Give the Post the Realm of the author's Organisation
        db = current.db
        utable = db.auth_user
        otable = current.s3db.org_organisation
        if "created_by" in row:
            query = (utable.id == row.created_by) & \
                    (otable.id == utable.organisation_id)
        else:
            query = (table.id == row.id) & \
                    (utable.id == table.created_by) & \
                    (otable.id == utable.organisation_id)
        org = db(query).select(otable.pe_id,
                               limitby=(0, 1)).first()
        if org:
            return org.pe_id

    # Follow normal rules
    return 0

settings.auth.realm_entity = drmp_realm_entity

# -----------------------------------------------------------------------------
# Pre-Populate
settings.base.prepopulate = ["Syria"]

settings.base.system_name = T("Syria Disaster Risk Management Information System ")
settings.base.system_name_short = T("DRMIS")

# -----------------------------------------------------------------------------
# Theme (folder to use for views/layout.html)
settings.base.theme = "Syria"
settings.ui.formstyle_row = "bootstrap"
settings.ui.formstyle = "bootstrap"
#settings.gis.map_height = 600
#settings.gis.map_width = 854

# -----------------------------------------------------------------------------
# L10n (Localization) settings
settings.L10n.languages = OrderedDict([
    ("ar", "العربية"),
    ("en", "English"),
])
# Default Language
settings.L10n.default_language = "en"
# Default timezone for users
settings.L10n.utc_offset = "UTC +0200"
# Unsortable 'pretty' date format
settings.L10n.date_format = "%d %b %y"
# Number formats (defaults to ISO 31-0)
# Decimal separator for numbers (defaults to ,)
settings.L10n.decimal_separator = "."
# Thousands separator for numbers (defaults to space)
settings.L10n.thousands_separator = ","

# Uncomment this to Translate CMS Series Names
# - we want this on when running s3translate but off in normal usage as we use the English names to lookup icons in render_posts
#settings.L10n.translate_cms_series = True
# Uncomment this to Translate Location Names
settings.L10n.translate_gis_location = True

# Restrict the Location Selector to just certain countries
settings.gis.countries = ["SY", "IQ", "LB", "TR", "JO", "EG", "DZ"]

# Until we add support to LocationSelector2 to set dropdowns from LatLons
#settings.gis.check_within_parent_boundaries = False
# Uncomment to hide Layer Properties tool
#settings.gis.layer_properties = False
# Hide unnecessary Toolbar items
settings.gis.nav_controls = False
# Uncomment to display the Map Legend as a floating DIV
settings.gis.legend = "float"

# -----------------------------------------------------------------------------
# Finance settings
settings.fin.currencies = {
    "CHF" : T("Swiss Francs"),
    "EUR" : T("Euros"),
    "GBP" : T("Great British Pounds"),
    "USD" : T("United States Dollars"),
}

# -----------------------------------------------------------------------------
# Enable this for a UN-style deployment
#settings.ui.cluster = True
# Enable this to use the label 'Camp' instead of 'Shelter'
settings.ui.camp = True

# -----------------------------------------------------------------------------
# Uncomment to restrict the export formats available
settings.ui.export_formats = ["xls"]

settings.ui.update_label = "Edit"

# -----------------------------------------------------------------------------
# Summary Pages
settings.ui.summary = [#{"common": True,
                       # "name": "cms",
                       # "widgets": [{"method": "cms"}]
                       # },
                       {"name": "map",
                        "label": "Map",
                        "widgets": [{"method": "map", "ajax_init": True}],
                        },
                       {"name": "charts",
                        "label": "Charts",
                        "widgets": [{"method": "report2", "ajax_init": True}]
                        },
                       {"name": "table",
                        "label": "Table",
                        "widgets": [{"method": "datatable"}]
                        },
                       ]

settings.ui.filter_auto_submit = 750
settings.ui.report_auto_submit = 750

settings.search.filter_manager = False

# =============================================================================
# Module Settings

# -----------------------------------------------------------------------------
# Human Resource Management
settings.hrm.staff_label = "Contacts"
# Uncomment to allow Staff & Volunteers to be registered without an email address
settings.hrm.email_required = False
# Uncomment to show the Organisation name in HR represents
settings.hrm.show_organisation = True
# Uncomment to disable Staff experience
settings.hrm.staff_experience = False
# Uncomment to disable the use of HR Credentials
settings.hrm.use_credentials = False
# Uncomment to disable the use of HR Skills
settings.hrm.use_skills = False
# Uncomment to disable the use of HR Teams
settings.hrm.teams = False

# Uncomment to hide fields in S3AddPersonWidget[2]
settings.pr.request_dob = False
settings.pr.request_gender = False

# -----------------------------------------------------------------------------
# Org
settings.org.site_label = "Office"

# -----------------------------------------------------------------------------
# Project
# Uncomment this to use multiple Organisations per project
settings.project.multiple_organisations = True

# Links to Filtered Components for Donors & Partners
#settings.project.organisation_roles = {
#    1: T("Host National Society"),
#    2: T("Partner"),
#    3: T("Donor"),
#    #4: T("Customer"), # T("Beneficiary")?
#    #5: T("Supplier"),
#    9: T("Partner National Society"),
#}

# -----------------------------------------------------------------------------
# Notifications
# Template for the subject line in update notifications
#settings.msg.notify_subject = "$S %s" % T("Notification")
settings.msg.notify_subject = "$S Notification"

# -----------------------------------------------------------------------------
def currency_represent(v):
    """
        Custom Representation of Currencies
    """

    if v == "USD":
        return "$"
    elif v == "EUR":
        return "€"
    elif v == "GBP":
        return "£"
    else:
        # e.g. CHF
        return v

# -----------------------------------------------------------------------------
def render_contacts(listid, resource, rfields, record, **attr):
    """
        Custom dataList item renderer for Contacts on the Profile pages

        @param listid: the HTML ID for this list
        @param resource: the S3Resource to render
        @param rfields: the S3ResourceFields to render
        @param record: the record as dict
        @param attr: additional HTML attributes for the item
    """

    pkey = "hrm_human_resource.id"

    # Construct the item ID
    if pkey in record:
        record_id = record[pkey]
        item_id = "%s-%s" % (listid, record_id)
    else:
        # template
        item_id = "%s-[id]" % listid

    item_class = "thumbnail"

    raw = record._row
    #author = record["hrm_human_resource.modified_by"]
    date = record["hrm_human_resource.modified_on"]
    fullname = record["hrm_human_resource.person_id"]
    job_title = raw["hrm_human_resource.job_title_id"] or ""
    if job_title:
        job_title = "- %s" % record["hrm_human_resource.job_title_id"]
    #organisation = record["hrm_human_resource.organisation_id"]
    organisation_id = raw["hrm_human_resource.organisation_id"]
    #org_url = URL(c="org", f="organisation", args=[organisation_id, "profile"])
    pe_id = raw["pr_person.pe_id"]
    person_id = raw["hrm_human_resource.person_id"]
    location = record["org_site.location_id"]
    location_id = raw["org_site.location_id"]
    location_url = URL(c="gis", f="location",
                       args=[location_id, "profile"])
    address = raw["gis_location.addr_street"] or T("no office assigned")
    email = raw["pr_email_contact.value"] or T("no email address")
    if isinstance(email, list):
        email = email[0]
    phone = raw["pr_phone_contact.value"] or T("no phone number")
    if isinstance(phone, list):
        phone = phone[0]

    db = current.db
    s3db = current.s3db
    ltable = s3db.pr_person_user
    query = (ltable.pe_id == pe_id)
    row = db(query).select(ltable.user_id,
                           limitby=(0, 1)
                           ).first()
    if row:
        # Use Personal Avatar
        # @ToDo: Optimise by not doing DB lookups (especially duplicate) within render, but doing these in the bulk query
        avatar = s3_avatar_represent(row.user_id,
                                     _class="media-object")
    else:
        avatar = IMG(_src=URL(c="static", f="img", args="blank-user.gif"),
                     _class="media-object")

    # Edit Bar
    permit = current.auth.s3_has_permission
    table = db.pr_person
    if permit("update", table, record_id=person_id):
        vars = {"refresh": listid,
                "record": record_id,
                }
        f = current.request.function
        if f == "organisation" and organisation_id:
            vars["(organisation)"] = organisation_id
        edit_url = URL(c="hrm", f="person",
                       args=[person_id, "update.popup"],
                       vars=vars)
        title_update = current.response.s3.crud_strings.hrm_human_resource.title_update
        edit_btn = A(I(" ", _class="icon icon-edit"),
                     _href=edit_url,
                     _class="s3_modal",
                     _title=title_update,
                     )
    else:
        edit_btn = ""
        edit_url = "#"
        title_update = ""
    # Deletions failing due to Integrity Errors
    #if permit("delete", table, record_id=person_id):
    #    delete_btn = A(I(" ", _class="icon icon-remove-sign"),
    #                   _class="dl-item-delete",
    #                   )
    #else:
    delete_btn = ""
    edit_bar = DIV(edit_btn,
                   delete_btn,
                   _class="edit-bar fright",
                   )

    avatar = A(avatar,
               _href=edit_url,
               _class="pull-left s3_modal",
               _title=title_update,
               )

    # Render the item
    body = TAG[""](P(fullname,
                     " ",
                     SPAN(job_title),
                     _class="person_pos",
                     ),
                   P(I(_class="icon-phone"),
                     " ",
                     SPAN(phone),
                     " ",
                     I(_class="icon-envelope-alt"),
                     " ",
                     SPAN(email),
                     _class="main_contact_ph",
                     ),
                   P(I(_class="icon-home"),
                     " ",
                     address,
                     _class="main_office-add",
                     ))

    item = DIV(DIV(SPAN(" ", _class="card-title"),
                   SPAN(A(location,
                          _href=location_url,
                          ),
                        _class="location-title",
                        ),
                   SPAN(date,
                        _class="date-title",
                        ),
                   edit_bar,
                   _class="card-header",
                   ),
               DIV(avatar,
                   DIV(DIV(body,
                           # Organisation only needed if displaying elsewhere than org profile
                           # Author confusing with main contact record
                           #DIV(#author,
                           #    #" - ",
                           #    A(organisation,
                           #      _href=org_url,
                           #      _class="card-organisation",
                           #      ),
                           #    _class="card-person",
                           #    ),
                           _class="media",
                           ),
                       _class="media-body",
                       ),
                   _class="media",
                   ),
               #docs,
               _class=item_class,
               _id=item_id,
               )

    return item

# -----------------------------------------------------------------------------
def render_events(listid, resource, rfields, record, **attr):
    """
        Custom dataList item renderer for Events on the Disaster Selection Page

        @param listid: the HTML ID for this list
        @param resource: the S3Resource to render
        @param rfields: the S3ResourceFields to render
        @param record: the record as dict
        @param attr: additional HTML attributes for the item
    """

    pkey = "event_event.id"

    # Construct the item ID
    if pkey in record:
        record_id = record[pkey]
        item_id = "%s-%s" % (listid, record_id)
    else:
        # template
        item_id = "%s-[id]" % listid

    item_class = "thumbnail"

    raw = record._row
    name = record["event_event.name"]
    date = record["event_event.zero_hour"]
    closed = raw["event_event.closed"]
    event_type = record["event_event_type.name"]
    event_url = URL(c="event", f="event",
                    args=[record_id, "profile"])
    comments = raw["event_event.comments"] or ""

    if closed:
        edit_bar = DIV()
    else:
        item_class = "%s disaster" % item_class

        permit = current.auth.s3_has_permission
        table = resource.table
        if permit("update", table, record_id=record_id):
            edit_btn = A(I(" ", _class="icon icon-edit"),
                         _href=URL(c="event", f="event",
                                   args=[record_id, "update.popup"],
                                   vars={"refresh": listid,
                                         "record": record_id}),
                         _class="s3_modal",
                         _title=current.response.s3.crud_strings.event_event.title_update,
                         )
        else:
            edit_btn = ""
        if permit("delete", table, record_id=record_id):
            delete_btn = A(I(" ", _class="icon icon-remove-sign"),
                           _class="dl-item-delete",
                          )
        else:
            delete_btn = ""
        edit_bar = DIV(edit_btn,
                       delete_btn,
                       _class="edit-bar fright",
                       )

    # Tallies
    tally_alerts = 0
    tally_incidents = 0
    tally_assessments = 0
    tally_activities = 0
    tally_reports = 0
    db = current.db
    s3db = current.s3db
    ltable = s3db.event_event_post
    table = db.cms_post
    stable = db.cms_series
    types = ["Incident", "Assessment", "Report"]
    query = (table.deleted == False) & \
            (ltable.event_id == record_id) & \
            (ltable.post_id == table.id) & \
            (stable.id == table.series_id) & \
            (stable.name.belongs(types))
    rows = db(query).select(stable.name)
    for row in rows:
        series = row.name
        if series == "Incident":
            tally_incidents += 1
        elif series == "Assessment":
            tally_assessments += 1
        elif series == "Report":
            tally_reports += 1

    # Render the item
    item = DIV(DIV(A(IMG(_class="media-object",
                         _src=URL(c="static",
                                  f="themes",
                                  args=["DRMP", "img", "%s.png" % event_type]),
                         ),
                     _class="pull-left",
                     _href=event_url,
                     ),
  		           DIV(SPAN(A(name,
                              _href=event_url,
                              _class="media-heading"
                              ),
                            ),
                       SPAN(date,
                            _class="date-title",
                            ),
                       edit_bar,
                       _class="card-header-select",
                       ),
                   DIV(P(comments),
                       P(T("Incidents"),
                         SPAN(tally_incidents,
                              _class="badge badge-warning",
                              ),
                         T("Assessments"),
                         SPAN(tally_assessments,
                              _class="badge",
                              ),
                        T("Reports"),
                         SPAN(tally_reports,
                              _class="badge",
                              ),
                         _class="tally",
                         ),
                       _class="media-body",
                       ),
                   _class="media",
                   ),
               _class=item_class,
               _id=item_id,
               )

    return item

# -----------------------------------------------------------------------------
def quote_unicode(s):
    """
        Quote unicode strings for URLs for Rocket
    """

    chars = []
    for char in s:
        o = ord(char)
        if o < 128:
            chars.append(char)
        else:
            chars.append(hex(o).replace("0x", "%").upper())
    return "".join(chars)

# -----------------------------------------------------------------------------
def render_locations(listid, resource, rfields, record, **attr):
    """
        Custom dataList item renderer for Locations on the Selection Page

        @param listid: the HTML ID for this list
        @param resource: the S3Resource to render
        @param rfields: the S3ResourceFields to render
        @param record: the record as dict
        @param attr: additional HTML attributes for the item
    """

    pkey = "gis_location.id"

    # Construct the item ID
    if pkey in record:
        record_id = record[pkey]
        item_id = "%s-%s" % (listid, record_id)
    else:
        # template
        item_id = "%s-[id]" % listid

    item_class = "thumbnail"

    raw = record._row
    name = raw["gis_location.name"]
    level = raw["gis_location.level"]
    L1 = raw["gis_location.L1"]
    L2 = raw["gis_location.L2"]
    L3 = raw["gis_location.L3"]
    location_url = URL(c="gis", f="location",
                       args=[record_id, "profile"])

    if level == "L1":
        represent = name
    if level == "L2":
        represent = "%s (%s)" % (name, L1)
    elif level == "L3":
        represent = "%s (%s, %s)" % (name, L2, L1)
    else:
        # L0 or specific
        represent = name

    # Users don't edit locations
    # permit = current.auth.s3_has_permission
    # table = current.db.gis_location
    # if permit("update", table, record_id=record_id):
        # edit_btn = A(I(" ", _class="icon icon-edit"),
                     # _href=URL(c="gis", f="location",
                               # args=[record_id, "update.popup"],
                               # vars={"refresh": listid,
                                     # "record": record_id}),
                     # _class="s3_modal",
                     # _title=current.response.s3.crud_strings.gis_location.title_update,
                     # )
    # else:
        # edit_btn = ""
    # if permit("delete", table, record_id=record_id):
        # delete_btn = A(I(" ", _class="icon icon-remove-sign"),
                       # _class="dl-item-delete",
                      # )
    # else:
        # delete_btn = ""
    # edit_bar = DIV(edit_btn,
                   # delete_btn,
                   # _class="edit-bar fright",
                   # )

    # Tallies
    # NB We assume that all records are readable here
    # Search all sub-locations
    locations = current.gis.get_children(record_id)
    locations = [l.id for l in locations]
    locations.append(record_id)
    db = current.db
    s3db = current.s3db
    ltable = s3db.project_location
    table = db.project_project
    query = (table.deleted == False) & \
            (ltable.deleted == False) & \
            (ltable.project_id == table.id) & \
            (ltable.location_id.belongs(locations))
    rows = db(query).select(table.id, distinct=True)
    tally_projects = len(rows)
    tally_incidents = 0
    tally_activities = 0
    tally_reports = 0
    table = s3db.cms_post
    stable = db.cms_series
    types = ["Incident", "Activity", "Report"]
    query = (table.deleted == False) & \
            (table.location_id.belongs(locations)) & \
            (stable.id == table.series_id) & \
            (stable.name.belongs(types))
    rows = db(query).select(stable.name)
    for row in rows:
        series = row.name
        if series == "Incident":
            tally_incidents += 1
        elif series == "Activity":
            tally_activities += 1
        elif series == "Report":
            tally_reports += 1

    # Build the icon, if it doesn't already exist
    filename = "%s.svg" % record_id
    import os
    filepath = os.path.join(current.request.folder, "static", "cache", "svg", filename)
    if not os.path.exists(filepath):
        gtable = db.gis_location
        loc = db(gtable.id == record_id).select(gtable.wkt,
                                                limitby=(0, 1)
                                                ).first()
        if loc:
            from s3.codecs.svg import S3SVG
            S3SVG.write_file(filename, loc.wkt)

    # Render the item
    item = DIV(DIV(A(IMG(_class="media-object",
                         _src=URL(c="static",
                                  f="cache",
                                  args=["svg", filename],
                                  )
                         ),
                     _class="pull-left",
                     _href=location_url,
                     ),
                   DIV(SPAN(A(represent,
                              _href=location_url,
                              _class="media-heading"
                              ),
                            ),
                       #edit_bar,
                       _class="card-header-select",
                       ),
                   DIV(P(T("Incidents"),
                         SPAN(tally_incidents,
                              _class="badge",
                              ),
                         T("Reports"),
                         SPAN(tally_reports,
                              _class="badge",
                              ),
                         T("Projects"),
                         SPAN(tally_projects,
                              _class="badge",
                              ),
                         T("Activities"),
                         SPAN(tally_activities,
                              _class="badge",
                              ),
                         _class="tally",
                         ),
                       _class="media-body",
                       ),
                   _class="media",
                   ),
               _class=item_class,
               _id=item_id,
               )

    return item

# -----------------------------------------------------------------------------
def render_locations_profile(listid, resource, rfields, record, **attr):
    """
        Custom dataList item renderer for Locations on the Profile Page
        - UNUSED

        @param listid: the HTML ID for this list
        @param resource: the S3Resource to render
        @param rfields: the S3ResourceFields to render
        @param record: the record as dict
        @param attr: additional HTML attributes for the item
    """

    pkey = "gis_location.id"

    # Construct the item ID
    if pkey in record:
        record_id = record[pkey]
        item_id = "%s-%s" % (listid, record_id)
    else:
        # template
        item_id = "%s-[id]" % listid

    item_class = "thumbnail"

    raw = record._row
    name = record["gis_location.name"]
    location_url = URL(c="gis", f="location",
                       args=[record_id, "profile"])

    # Placeholder to maintain style
    #logo = DIV(IMG(_class="media-object"),
    #               _class="pull-left")

    # We don't Edit Locations
    # Edit Bar
    # permit = current.auth.s3_has_permission
    # table = current.db.gis_location
    # if permit("update", table, record_id=record_id):
        # vars = {"refresh": listid,
                # "record": record_id,
                # }
        # f = current.request.function
        # if f == "organisation" and organisation_id:
            # vars["(organisation)"] = organisation_id
        # edit_btn = A(I(" ", _class="icon icon-edit"),
                     # _href=URL(c="gis", f="location",
                               # args=[record_id, "update.popup"],
                               # vars=vars),
                     # _class="s3_modal",
                     # _title=current.response.s3.crud_strings.gis_location.title_update,
                     # )
    # else:
        # edit_btn = ""
    # if permit("delete", table, record_id=record_id):
        # delete_btn = A(I(" ", _class="icon icon-remove-sign"),
                       # _class="dl-item-delete",
                       # )
    # else:
        # delete_btn = ""
    # edit_bar = DIV(edit_btn,
                   # delete_btn,
                   # _class="edit-bar fright",
                   # )

    # Render the item
    item = DIV(DIV(DIV(#SPAN(A(name,
                       #       _href=location_url,
                       #       ),
                       #     _class="location-title"),
                       #" ",
                       #edit_bar,
                       P(A(name,
                           _href=location_url,
                           ),
                         _class="card_comments"),
                       _class="span5"), # card-details
                   _class="row",
                   ),
               )

    return item

# -----------------------------------------------------------------------------
def render_offices(listid, resource, rfields, record, **attr):
    """
        Custom dataList item renderer for Offices on the Profile pages

        @param listid: the HTML ID for this list
        @param resource: the S3Resource to render
        @param rfields: the S3ResourceFields to render
        @param record: the record as dict
        @param attr: additional HTML attributes for the item
    """

    pkey = "org_office.id"

    # Construct the item ID
    if pkey in record:
        record_id = record[pkey]
        item_id = "%s-%s" % (listid, record_id)
    else:
        # template
        item_id = "%s-[id]" % listid

    item_class = "thumbnail"

    raw = record._row
    name = record["org_office.name"]
    author = record["org_office.modified_by"]
    date = record["org_office.modified_on"]
    organisation = record["org_office.organisation_id"]
    organisation_id = raw["org_office.organisation_id"]
    location = record["org_office.location_id"]
    location_id = raw["org_office.location_id"]
    location_url = URL(c="gis", f="location",
                       args=[location_id, "profile"])
    address = raw["gis_location.addr_street"]
    office_type = record["org_office.office_type_id"]
    logo = raw["org_organisation.logo"]

    org_url = URL(c="org", f="organisation", args=[organisation_id, "profile"])
    if logo:
        logo = A(IMG(_src=URL(c="default", f="download", args=[logo]),
                     _class="media-object",
                     ),
                 _href=org_url,
                 _class="pull-left",
                 )
    else:
        logo = DIV(IMG(_class="media-object"),
                   _class="pull-left")

    # Edit Bar
    permit = current.auth.s3_has_permission
    table = current.db.org_office
    if permit("update", table, record_id=record_id):
        vars = {"refresh": listid,
                "record": record_id,
                }
        f = current.request.function
        if f == "organisation" and organisation_id:
            vars["(organisation)"] = organisation_id
        edit_btn = A(I(" ", _class="icon icon-edit"),
                     _href=URL(c="org", f="office",
                               args=[record_id, "update.popup"],
                               vars=vars),
                     _class="s3_modal",
                     _title=current.response.s3.crud_strings.org_office.title_update,
                     )
    else:
        edit_btn = ""
    if permit("delete", table, record_id=record_id):
        delete_btn = A(I(" ", _class="icon icon-remove-sign"),
                       _class="dl-item-delete",
                       )
    else:
        delete_btn = ""
    edit_bar = DIV(edit_btn,
                   delete_btn,
                   _class="edit-bar fright",
                   )

    # Render the item
    avatar = logo
    body = TAG[""](P(name),
                   P(I(_class="icon-flag"),
                     " ",
                     SPAN(office_type),
                     " ",
                     _class="main_contact_ph",
                     ),
                   P(I(_class="icon-home"),
                     " ",
                     address,
                     _class="main_office-add",
                     ))

    item = DIV(DIV(SPAN(" ", _class="card-title"),
                   SPAN(A(location,
                          _href=location_url,
                          ),
                        _class="location-title",
                        ),
                   SPAN(date,
                        _class="date-title",
                        ),
                   edit_bar,
                   _class="card-header",
                   ),
               DIV(avatar,
                   DIV(DIV(body,
                           DIV(author,
                               " - ",
                               A(organisation,
                                 _href=org_url,
                                 _class="card-organisation",
                                 ),
                               _class="card-person",
                               ),
                           _class="media",
                           ),
                       _class="media-body",
                       ),
                   _class="media",
                   ),
               #docs,
               _class=item_class,
               _id=item_id,
               )

    return item

# -----------------------------------------------------------------------------
def render_organisations(listid, resource, rfields, record, **attr):
    """
        Custom dataList item renderer for Organisations on the Stakeholder Selection Page

        @param listid: the HTML ID for this list
        @param resource: the S3Resource to render
        @param rfields: the S3ResourceFields to render
        @param record: the record as dict
        @param attr: additional HTML attributes for the item
    """

    pkey = "org_organisation.id"

    # Construct the item ID
    if pkey in record:
        record_id = record[pkey]
        item_id = "%s-%s" % (listid, record_id)
    else:
        # template
        item_id = "%s-[id]" % listid

    item_class = "thumbnail span6"

    raw = record._row
    name = record["org_organisation.name"]
    logo = raw["org_organisation.logo"]
    # @ToDo: Just take National offices
    addresses = raw["gis_location.addr_street"]
    if addresses:
        if isinstance(addresses, list):
            address = addresses[0]
        else:
            address = addresses
    else:
        address = ""
    phone = raw["org_organisation.phone"] or ""

    org_url = URL(c="org", f="organisation", args=[record_id, "profile"])
    if logo:
        logo = A(IMG(_src=URL(c="default", f="download", args=[logo]),
                     _class="media-object",
                     ),
                 _href=org_url,
                 _class="pull-left",
                 )
    else:
        logo = DIV(IMG(_class="media-object"),
                   _class="pull-left")

    permit = current.auth.s3_has_permission
    table = current.db.org_organisation
    if permit("update", table, record_id=record_id):
        edit_btn = A(I(" ", _class="icon icon-edit"),
                     _href=URL(c="org", f="organisation",
                               args=[record_id, "update.popup"],
                               vars={"refresh": listid,
                                     "record": record_id}),
                     _class="s3_modal",
                     _title=current.response.s3.crud_strings.org_organisation.title_update,
                     )
    else:
        edit_btn = ""
    if permit("delete", table, record_id=record_id):
        delete_btn = A(I(" ", _class="icon icon-remove-sign"),
                       _class="dl-item-delete",
                      )
    else:
        delete_btn = ""
    edit_bar = DIV(edit_btn,
                   delete_btn,
                   _class="edit-bar fright",
                   )

    # Tallies
    # NB We assume that all records are readable here
    db = current.db
    s3db = current.s3db
    table = s3db.project_project
    query = (table.deleted == False) & \
            (table.organisation_id == record_id)
    tally_projects = db(query).count()
    tally_assessments = 0
    tally_activities = 0
    tally_reports = 0
    table = s3db.cms_post
    atable = db.auth_user
    stable = db.cms_series
    types = ["Assessment", "Activity", "Report"]
    query = (table.deleted == False) & \
            (table.created_by == atable.id) & \
            (atable.organisation_id == record_id) & \
            (stable.id == table.series_id) & \
            (stable.name.belongs(types))
    rows = db(query).select(stable.name)
    for row in rows:
        series = row.name
        if series == "Assessment":
            tally_assessments += 1
        elif series == "Activity":
            tally_activities += 1
        elif series == "Report":
            tally_reports += 1
    
    # Render the item
    item = DIV(DIV(logo,
                   DIV(SPAN(A(name,
                              _href=org_url,
                              _class="media-heading"
                              ),
                            ),
                       edit_bar,
                       _class="card-header-select",
                       ),
                   DIV(P(I(_class="icon icon-phone"),
                         " ",
                         phone,
                         _class="main_contact_ph",
                         ),
                       P(I(_class="icon icon-home"),
                         " ",
                         address,
                         _class="main_office-add",
                         ),
                       P(T("Projects"),
                         SPAN(tally_projects,
                              _class="badge",
                              ),
                         T("Activities"),
                         SPAN(tally_activities,
                              _class="badge",
                              ),
                         T("Reports"),
                         SPAN(tally_reports,
                              _class="badge",
                              ),
                         T("Assessments"),
                         SPAN(tally_assessments,
                              _class="badge",
                              ),
                         _class="tally",
                         ),
                       _class="media-body",
                       ),
                   _class="media",
                   ),
               _class=item_class,
               _id=item_id,
               )

    return item

# -----------------------------------------------------------------------------
def render_posts(listid, resource, rfields, record, 
                 type = None,
                 **attr):
    """
        Custom dataList item renderer for CMS Posts on the Home & News Feed pages

        @param listid: the HTML ID for this list
        @param resource: the S3Resource to render
        @param rfields: the S3ResourceFields to render
        @param record: the record as dict
        @param attr: additional HTML attributes for the item
    """

    pkey = "cms_post.id"

    # Construct the item ID
    if pkey in record:
        record_id = record[pkey]
        item_id = "%s-%s" % (listid, record_id)
    else:
        # template
        item_id = "%s-[id]" % listid

    item_class = "thumbnail"

    raw = record._row
    series = record["cms_post.series_id"]
    date = record["cms_post.date"]
    body = record["cms_post.body"]
    location = record["cms_post.location_id"]
    location_id = raw["cms_post.location_id"]
    location_url = URL(c="gis", f="location", args=[location_id, "profile"])
    author = record["cms_post.created_by"]
    author_id = raw["cms_post.created_by"]
    organisation = record["auth_user.organisation_id"]
    organisation_id = raw["auth_user.organisation_id"]
    org_url = URL(c="org", f="organisation", args=[organisation_id, "profile"])

    db = current.db
    s3db = current.s3db
    ltable = s3db.pr_person_user
    ptable = db.pr_person
    query = (ltable.user_id == author_id) & \
            (ltable.pe_id == ptable.pe_id)
    row = db(query).select(ptable.id,
                           limitby=(0, 1)
                           ).first()
    if row:
        person_url = URL(c="hrm", f="person", args=[row.id])
    else:
        person_url = "#"
    author = A(author,
               _href=person_url,
               )

    # Use Personal Avatar
    # @ToDo: Optimise by not doing DB lookups (especially duplicate) within render, but doing these in the bulk query
    #avatar = s3_avatar_represent(author_id,
    #                             _class="media-object")
    #avatar = A(avatar,
    #           _href=person_url,
    #           _class="pull-left",
    #           )

    # Use Organisation Logo
    otable = db.org_organisation
    row = db(otable.id == organisation_id).select(otable.logo,
                                                  limitby=(0, 1)
                                                  ).first()
    if row and row.logo:
        logo = URL(c="default", f="download", args=[row.logo])
    else:
        logo = ""
    avatar = IMG(_src=logo,
                 _height=50,
                 _width=50,
                 _style="padding-right:5px;",
                 _class="media-object")
    avatar = A(avatar,
               _href=org_url,
               _class="pull-left",
               )

    # Edit Bar
    permit = current.auth.s3_has_permission
    table = db.cms_post
    if permit("update", table, record_id=record_id):
        edit_btn = A(I(" ", _class="icon icon-edit"),
                     _href=URL(c="cms", f="post",
                               args=[record_id, "update.popup"],
                               vars={"refresh": listid,
                                     "record": record_id}),
                     _class="s3_modal",
                     _title=T("Edit %(type)s") % dict(type=T(series)),
                     )
    else:
        edit_btn = ""
    if permit("delete", table, record_id=record_id):
        delete_btn = A(I(" ", _class="icon icon-remove-sign"),
                       _class="dl-item-delete",
                       )
    else:
        delete_btn = ""
    edit_bar = DIV(edit_btn,
                   delete_btn,
                   _class="edit-bar fright",
                   )

    # Dropdown of available documents
    documents = raw["doc_document.file"]
    if documents:
        if not isinstance(documents, list):
            documents = [documents]
        doc_list = UL(_class="dropdown-menu",
                      _role="menu",
                      )
        retrieve = db.doc_document.file.retrieve
        for doc in documents:
            try:
                doc_name = retrieve(doc)[0]
            except IOError:
                doc_name = current.messages["NONE"]
            doc_url = URL(c="default", f="download",
                          args=[doc])
            doc_item = LI(A(I(_class="icon-file"),
                            " ",
                            doc_name,
                            _href=doc_url,
                            ),
                          _role="menuitem",
                          )
            doc_list.append(doc_item)
        docs = DIV(A(I(_class="icon-paper-clip"),
                     SPAN(_class="caret"),
                     _class="btn dropdown-toggle",
                     _href="#",
                     **{"_data-toggle": "dropdown"}
                     ),
                   doc_list,
                   _class="btn-group attachments dropdown pull-right",
                   )
    else:
        docs = ""

    if current.request.controller == "default":
        # Mixed resource lists (Home, News Feed)
        icon = series.lower().replace(" ", "_")
        card_label = TAG[""](I(_class="icon icon-%s" % icon),
                             SPAN(" %s" % T(series),
                                  _class="card-title"))
        # Type cards
        if series == "Incident": 
            # Apply additional highlighting for Incidents
            item_class = "%s disaster" % item_class
    else:
        card_label = SPAN(" ", _class="card-title")

    # Render the item
    if "newsfeed" not in current.request.args and series == "Event":
        item = DIV(DIV(SPAN(date,
                            _class="date-title event",
                            ),
                       SPAN(A(location,
                              _href=location_url,
                              ),
                            _class="location-title",
                            ),
                       edit_bar,
                       _class="card-header",
                       ),
                   DIV(avatar,
                       DIV(DIV(body,
                               DIV(author,
                                   " - ",
                                   A(organisation,
                                     _href=org_url,
                                     _class="card-organisation",
                                     ),
                                   _class="card-person",
                                   ),
                               _class="media",
                               ),
                           _class="media-body",
                           ),
                       _class="media",
                       ),
                   docs,
                   _class=item_class,
                   _id=item_id,
                   )
    else:
        item = DIV(DIV(card_label,
                       SPAN(A(location,
                              _href=location_url,
                              ),
                            _class="location-title",
                            ),
                       SPAN(date,
                            _class="date-title",
                            ),
                       edit_bar,
                       _class="card-header",
                       ),
                   DIV(avatar,
                       DIV(DIV(body,
                               DIV(author,
                                   " - ",
                                   A(organisation,
                                     _href=org_url,
                                     _class="card-organisation",
                                     ),
                                   _class="card-person",
                                   ),
                               _class="media",
                               ),
                           _class="media-body",
                           ),
                       _class="media",
                       ),
                   docs,
                   _class=item_class,
                   _id=item_id,
                   )

    return item

s3.render_posts = render_posts

# -----------------------------------------------------------------------------
def render_profile_posts(listid, resource, rfields, record, **attr):
    """
        Custom dataList item renderer for CMS Posts on the Profile pages

        @param listid: the HTML ID for this list
        @param resource: the S3Resource to render
        @param rfields: the S3ResourceFields to render
        @param record: the record as dict
        @param attr: additional HTML attributes for the item
    """

    pkey = "cms_post.id"

    # Construct the item ID
    if pkey in record:
        record_id = record[pkey]
        item_id = "%s-%s" % (listid, record_id)
    else:
        # template
        item_id = "%s-[id]" % listid

    item_class = "thumbnail"

    raw = record._row
    series = record["cms_post.series_id"]
    date = record["cms_post.date"]
    body = record["cms_post.body"]
    event_id = raw["event_event_post.event_id"]
    location = record["cms_post.location_id"]
    location_id = raw["cms_post.location_id"]
    location_url = URL(c="gis", f="location", args=[location_id, "profile"])
    author = record["cms_post.created_by"]
    author_id = raw["cms_post.created_by"]
    organisation = record["auth_user.organisation_id"]
    organisation_id = raw["auth_user.organisation_id"]
    org_url = URL(c="org", f="organisation", args=[organisation_id, "profile"])

    db = current.db
    s3db = current.s3db
    ltable = s3db.pr_person_user
    ptable = db.pr_person
    query = (ltable.user_id == author_id) & \
            (ltable.pe_id == ptable.pe_id)
    row = db(query).select(ptable.id,
                           limitby=(0, 1)
                           ).first()
    if row:
        person_url = URL(c="hrm", f="person", args=[row.id])
    else:
        person_url = "#"
    author = A(author,
               _href=person_url,
               )

    # Use Personal Avatar
    # @ToDo: Optimise by not doing DB lookups (especially duplicate) within render, but doing these in the bulk query
    #avatar = s3_avatar_represent(author_id,
    #                             _class="media-object")
    #avatar = A(avatar,
    #           _href=person_url,
    #           _class="pull-left",
    #           )

    # Use Organisation Logo
    otable = db.org_organisation
    row = db(otable.id == organisation_id).select(otable.logo,
                                                  limitby=(0, 1)
                                                  ).first()
    if row and row.logo:
        logo = URL(c="default", f="download", args=[row.logo])
    else:
        logo = ""
    avatar = IMG(_src=logo,
                 _height=50,
                 _width=50,
                 #_style="padding-right:5px;",
                 _class="media-object")
    avatar = A(avatar,
               _href=org_url,
               _class="pull-left",
               )

    # Edit Bar
    permit = current.auth.s3_has_permission
    table = db.cms_post
    if permit("update", table, record_id=record_id):
        T = current.T
        vars = {"refresh": listid,
                "record": record_id,
                "~.series_id$name": series,
                }
        f = current.request.function
        if f == "event" and event_id:
            vars["(event)"] = event_id
        if f == "location" and location_id:
            vars["(location)"] = location_id
        edit_btn = A(I(" ", _class="icon icon-edit"),
                     _href=URL(c="cms", f="post",
                               args=[record_id, "update.popup"],
                               vars=vars),
                     _class="s3_modal",
                     _title=T("Edit %(type)s") % dict(type=T(series)),
                     )
    else:
        edit_btn = ""
    if permit("delete", table, record_id=record_id):
        delete_btn = A(I(" ", _class="icon icon-remove-sign"),
                       _class="dl-item-delete",
                       )
    else:
        delete_btn = ""
    edit_bar = DIV(edit_btn,
                   delete_btn,
                   _class="edit-bar fright",
                   )

    # Dropdown of available documents
    documents = raw["doc_document.file"]
    if documents:
        if not isinstance(documents, list):
            documents = [documents]
        doc_list = UL(_class="dropdown-menu",
                      _role="menu",
                      )
        retrieve = db.doc_document.file.retrieve
        for doc in documents:
            try:
                doc_name = retrieve(doc)[0]
            except IOError:
                doc_name = current.messages["NONE"]
            doc_url = URL(c="default", f="download",
                          args=[doc])
            doc_item = LI(A(I(_class="icon-file"),
                            " ",
                            doc_name,
                            _href=doc_url,
                            ),
                          _role="menuitem",
                          )
            doc_list.append(doc_item)
        docs = DIV(A(I(_class="icon-paper-clip"),
                     SPAN(_class="caret"),
                     _class="btn dropdown-toggle",
                     _href="#",
                     **{"_data-toggle": "dropdown"}
                     ),
                   doc_list,
                   _class="btn-group attachments dropdown pull-right",
                   )
    else:
        docs = ""

    # Render the item
    class SMALL(DIV):
        tag = "small"

    item = DIV(DIV(DIV(avatar,
                       P(SMALL(" ", author, " ",
                               A(organisation,
                                 _href=org_url,
                                 _class="card-organisation",
                                 ),
                               ),
                         _class="citation"),
                       _class="span1"),
                   DIV(SPAN(A(location,
                              _href=location_url,
                              ),
                            _class="location-title"),
                       " ",
                       SPAN(date,
                            _class="date-title"),
                       edit_bar,
                       P(body,
                         _class="card_comments"),
                       docs,
                       _class="span5 card-details"),
                   _class="row",
                   ),
               _class=item_class,
               _id=item_id,
               )

    return item

# -----------------------------------------------------------------------------
def render_projects(listid, resource, rfields, record, **attr):
    """
        Custom dataList item renderer for Projects on the Profile pages

        @param listid: the HTML ID for this list
        @param resource: the S3Resource to render
        @param rfields: the S3ResourceFields to render
        @param record: the record as dict
        @param attr: additional HTML attributes for the item
    """

    pkey = "project_project.id"

    # Construct the item ID
    if pkey in record:
        record_id = record[pkey]
        item_id = "%s-%s" % (listid, record_id)
    else:
        # template
        item_id = "%s-[id]" % listid

    item_class = "thumbnail"

    raw = record._row
    name = record["project_project.name"]
    author = record["project_project.modified_by"]
    author_id = raw["project_project.modified_by"]
    contact = record["project_project.human_resource_id"]
    date = record["project_project.modified_on"]
    organisation = record["project_project.organisation_id"]
    organisation_id = raw["project_project.organisation_id"]
    location = record["project_location.location_id"]
    location_ids = raw["project_location.location_id"]
    if isinstance(location_ids, list):
        locations = location.split(",")
        locations_list = []
        length = len(location_ids)
        i = 0
        for location_id in location_ids:
            location_url = URL(c="gis", f="location",
                               args=[location_id, "profile"])
            locations_list.append(A(locations[i], _href=location_url))
            i += 1
            if i != length:
                locations_list.append(",")
    else:
        location_url = URL(c="gis", f="location",
                           args=[location_ids, "profile"])
        locations_list = [A(location, _href=location_url)]

    logo = raw["org_organisation.logo"]
    org_url = URL(c="org", f="organisation", args=[organisation_id, "profile"])
    if logo:
        avatar = A(IMG(_src=URL(c="default", f="download", args=[logo]),
                       _class="media-object",
                       ),
                   _href=org_url,
                   _class="pull-left",
                   )
    else:
        avatar = DIV(IMG(_class="media-object"),
                     _class="pull-left")

    db = current.db
    s3db = current.s3db
    ltable = s3db.pr_person_user
    ptable = db.pr_person
    query = (ltable.user_id == author_id) & \
            (ltable.pe_id == ptable.pe_id)
    row = db(query).select(ptable.id,
                           limitby=(0, 1)
                           ).first()
    if row:
        person_url = URL(c="hrm", f="person", args=[row.id])
    else:
        person_url = "#"
    author = A(author,
               _href=person_url,
               )

    start_date = raw["project_project.start_date"] or ""
    if start_date:
        start_date = record["project_project.start_date"]
    end_date = raw["project_project.end_date"] or ""
    if end_date:
        end_date = record["project_project.end_date"]
    budget = record["project_project.budget"]
    if budget:
        budget = "USD %s" % budget

    partner = record["project_partner_organisation.organisation_id"]
    partner_ids = raw["project_partner_organisation.organisation_id"]
    if isinstance(partner_ids, list):
        partners = partner.split(",")
        partners_list = []
        length = len(partner_ids)
        i = 0
        for partner_id in partner_ids:
            partner_url = URL(c="org", f="organisation",
                              args=[partner_id, "profile"])
            partners_list.append(A(partners[i], _href=partner_url))
            i += 1
            if i != length:
                partners_list.append(",")
    elif partner_ids:
        partner_url = URL(c="org", f="organisation",
                          args=[partner_ids, "profile"])
        partners_list = [A(partner, _href=partner_url)]
    else:
        partners_list = [current.messages["NONE"]]

    donor = record["project_donor_organisation.organisation_id"]
    donor_ids = raw["project_donor_organisation.organisation_id"]
    if isinstance(donor_ids, list):
        donors = donor.split(",")
        amounts = raw["project_donor_organisation.amount"]
        if not isinstance(amounts, list):
            amounts = [amounts for donor_id in donor_ids]
        currencies = raw["project_donor_organisation.currency"]
        if not isinstance(currencies, list):
            currencies = [currencies for donor_id in donor_ids]
        amount_represent = IS_INT_AMOUNT.represent
        donors_list = []
        length = len(donor_ids)
        i = 0
        for donor_id in donor_ids:
            if donor_id:
                donor_url = URL(c="org", f="organisation",
                                args=[donor_id, "profile"])
                donor = A(donors[i], _href=donor_url)
                amount = amounts[i]
                if amount:
                    donor = TAG[""](donor,
                                    " - ",
                                    currency_represent(currencies[i]),
                                    amount_represent(amount))
            else:
                donor = current.messages["NONE"]
            donors_list.append(donor)
            i += 1
            if i != length:
                donors_list.append(",")
    elif donor_ids:
        donor_url = URL(c="org", f="organisation",
                      args=[donor_ids, "profile"])
        donors_list = [A(donor, _href=donor_url)]
    else:
        donors_list = [current.messages["NONE"]]

    # Edit Bar
    permit = current.auth.s3_has_permission
    table = current.db.project_project
    if permit("update", table, record_id=record_id):
        vars = {"refresh": listid,
                "record": record_id,
                }
        f = current.request.function
        if f == "organisation" and organisation_id:
            vars["(organisation)"] = organisation_id
        # "record not found" since multiples here
        #elif f == "location" and location_ids:
        #    vars["(location)"] = location_ids
        edit_btn = A(I(" ", _class="icon icon-edit"),
                     _href=URL(c="project", f="project",
                               args=[record_id, "update.popup"],
                               vars=vars),
                     _class="s3_modal",
                     _title=current.response.s3.crud_strings.project_project.title_update,
                     )
    else:
        # Read in Popup
        edit_btn = A(I(" ", _class="icon icon-search"),
                     _href=URL(c="project", f="project",
                               args=[record_id, "read.popup"]),
                     _class="s3_modal",
                     _title=current.response.s3.crud_strings.project_project.title_display,
                     )
    if permit("delete", table, record_id=record_id):
        delete_btn = A(I(" ", _class="icon icon-remove-sign"),
                       _class="dl-item-delete",
                       )
    else:
        delete_btn = ""
    edit_bar = DIV(edit_btn,
                   delete_btn,
                   _class="edit-bar fright",
                   )

    # Dropdown of available documents
    documents = raw["doc_document.file"]
    if documents:
        if not isinstance(documents, list):
            documents = [documents]
        doc_list = UL(_class="dropdown-menu",
                      _role="menu",
                      )
        retrieve = db.doc_document.file.retrieve
        for doc in documents:
            try:
                doc_name = retrieve(doc)[0]
            except IOError:
                doc_name = current.messages["NONE"]
            doc_url = URL(c="default", f="download",
                          args=[doc])
            doc_item = LI(A(I(_class="icon-file"),
                            " ",
                            doc_name,
                            _href=doc_url,
                            ),
                          _role="menuitem",
                          )
            doc_list.append(doc_item)
        docs = DIV(A(I(_class="icon-paper-clip"),
                     SPAN(_class="caret"),
                     _class="btn dropdown-toggle",
                     _href="#",
                     **{"_data-toggle": "dropdown"}
                     ),
                   doc_list,
                   _class="btn-group attachments dropdown pull-right",
                   )
    else:
        docs = ""

    # Render the item,
    body = TAG[""](P(I(_class="icon-user"),
                     " ",
                     STRONG("%s:" % T("Focal Point")),
                     " ",
                     contact,
                     _class="main_contact_ph"),
                   P(I(_class="icon-calendar"),
                     " ",
                     STRONG("%s:" % T("Start & End Date")),
                     " ",
                     T("%(start_date)s to %(end_date)s") % \
                            dict(start_date=start_date,
                            end_date = end_date),
                     _class="main_contact_ph"),
                   P(I(_class="icon-link"),
                     " ",
                     STRONG("%s:" % T("Partner")),
                     " ",
                     *partners_list,
                     _class="main_contact_ph"),
                   P(I(_class="icon-money"),
                     " ",
                     STRONG("%s:" % T("Donor")),
                     " ",
                     *donors_list,
                     _class="main_office-add")
                   )

    item = DIV(DIV(SPAN(" ", _class="card-title"),
                   SPAN(*locations_list,
                        _class="location-title"
                        ),
                   SPAN(date,
                        _class="date-title",
                        ),
                   edit_bar,
                   _class="card-header",
                   ),
               DIV(avatar,
                   DIV(DIV(body,
                           DIV(author,
                               " - ",
                               A(organisation,
                                 _href=org_url,
                                 _class="card-organisation",
                                 ),
                               _class="card-person",
                               ),
                           _class="media",
                           ),
                       _class="media-body",
                       ),
                   _class="media",
                   ),
               docs,
               _class=item_class,
               _id=item_id,
               )

    return item

# -----------------------------------------------------------------------------
def render_resources(listid, resource, rfields, record, **attr):
    """
        Custom dataList item renderer for Resources on the Profile pages

        @param listid: the HTML ID for this list
        @param resource: the S3Resource to render
        @param rfields: the S3ResourceFields to render
        @param record: the record as dict
        @param attr: additional HTML attributes for the item
    """

    pkey = "org_resource.id"

    # Construct the item ID
    if pkey in record:
        record_id = record[pkey]
        item_id = "%s-%s" % (listid, record_id)
    else:
        # template
        item_id = "%s-[id]" % listid

    item_class = "thumbnail"

    raw = record._row
    author = record["org_resource.modified_by"]
    date = record["org_resource.modified_on"]
    quantity = record["org_resource.value"]
    resource_type = record["org_resource.parameter_id"]
    body = "%s %s" % (quantity, resource_type)
    comments = raw["org_resource.comments"]
    organisation = record["org_resource.organisation_id"]
    organisation_id = raw["org_resource.organisation_id"]
    location = record["org_resource.location_id"]
    location_id = raw["org_resource.location_id"]
    location_url = URL(c="gis", f="location",
                       args=[location_id, "profile"])
    logo = raw["org_organisation.logo"]

    org_url = URL(c="org", f="organisation", args=[organisation_id, "profile"])
    if logo:
        logo = A(IMG(_src=URL(c="default", f="download", args=[logo]),
                     _class="media-object",
                     ),
                 _href=org_url,
                 _class="pull-left",
                 )
    else:
        logo = DIV(IMG(_class="media-object"),
                   _class="pull-left")

    # Edit Bar
    permit = current.auth.s3_has_permission
    table = current.db.org_resource
    if permit("update", table, record_id=record_id):
        vars = {"refresh": listid,
                "record": record_id,
                }
        f = current.request.function
        if f == "organisation" and organisation_id:
            vars["(organisation)"] = organisation_id
        elif f == "location" and location_id:
            vars["(location)"] = location_id
        edit_btn = A(I(" ", _class="icon icon-edit"),
                     _href=URL(c="org", f="resource",
                               args=[record_id, "update.popup"],
                               vars=vars),
                     _class="s3_modal",
                     _title=current.response.s3.crud_strings.org_resource.title_update,
                     )
    else:
        edit_btn = ""
    if permit("delete", table, record_id=record_id):
        delete_btn = A(I(" ", _class="icon icon-remove-sign"),
                       _class="dl-item-delete",
                       )
    else:
        delete_btn = ""
    edit_bar = DIV(edit_btn,
                   delete_btn,
                   _class="edit-bar fright",
                   )

    # Render the item
    avatar = logo
    body = TAG[""](body, BR(), comments)

    item = DIV(DIV(SPAN(" ", _class="card-title"),
                   SPAN(A(location,
                          _href=location_url,
                          ),
                        _class="location-title",
                        ),
                   SPAN(date,
                        _class="date-title",
                        ),
                   edit_bar,
                   _class="card-header",
                   ),
               DIV(avatar,
                   DIV(DIV(body,
                           DIV(author,
                               " - ",
                               A(organisation,
                                 _href=org_url,
                                 _class="card-organisation",
                                 ),
                               _class="card-person",
                               ),
                           _class="media",
                           ),
                       _class="media-body",
                       ),
                   _class="media",
                   ),
               #docs,
               _class=item_class,
               _id=item_id,
               )

    return item

# -----------------------------------------------------------------------------
def customize_cms_post_fields():
    """
        Customize cms_post fields for it's own controller & for Profile pages
    """

    s3db = current.s3db

    # Hide Labels when just 1 column in inline form
    s3db.doc_document.file.label = ""
    s3db.event_event_post.event_id.label = ""

    table = s3db.cms_post
    field = table.location_id
    field.label = ""
    field.represent = s3db.gis_LocationRepresent(sep=" | ")
    field.requires = IS_NULL_OR(
                        IS_LOCATION_SELECTOR2(levels=["L0", "L1", "L2", "L3"])
                     )
    field.widget = S3LocationSelectorWidget2(levels=["L0", "L1", "L2", "L3"])

    table.created_by.represent = s3_auth_user_represent_name

    list_fields = ["series_id",
                   "location_id",
                   "date",
                   "body",
                   "created_by",
                   "created_by$organisation_id",
                   "document.file",
                   #"event_post.event_id",
                   ]

    s3db.configure("cms_post",
                   list_fields = list_fields,
                   )

    return table
    
# -----------------------------------------------------------------------------
def cms_post_popup(r):
    """
        Customized Map popup for cms_post resource
        - style like the cards
        - currently unused
    """

    record = r.record
    pkey = "cms_post.id"

    # Construct the item ID
    map_id = "default_map" # @ToDo: provide the map_id as a var in order to be able to support multiple maps
    record_id = record[pkey]
    item_id = "%s-%s" % (map_id, record_id)

    item_class = "thumbnail"

    db = current.db
    table = db.cms_post

    series = table.series_id.represent(record.series_id)
    date = table.date.represent(record.date)
    body = record.body
    location_id = record.location_id
    location = table.location_id.represent(location_id)
    location_url = URL(c="gis", f="location", args=[location_id])
    author_id = record.created_by
    author = table.created_by.represent(author_id)

    s3db = current.s3db
    ltable = s3db.pr_person_user
    ptable = db.pr_person
    query = (ltable.user_id == author_id) & \
            (ltable.pe_id == ptable.pe_id)
    row = db(query).select(ptable.id,
                           limitby=(0, 1)
                           ).first()
    if row:
        person_url = URL(c="hrm", f="person", args=[row.id])
    else:
        person_url = "#"
    author = A(author,
               _href=person_url,
               )

    utable = db.auth_user
    otable = db.org_organisation
    query = (utable.id == author_id) & \
            (otable.id == utable.organisation_id)
    row = db(query).select(otable.id,
                           otable.name,
                           otable.logo,
                           limitby=(0, 1)
                           ).first()
    if row:
        organisation_id = row.id
        organisation = row.name
        org_url = URL(c="org", f="organisation", args=[organisation_id, "profile"])
        logo = URL(c="default", f="download", args=[row.logo])
    else:
        organisation_id = 0
        organisation = ""
        org_url = ""
        logo = ""

    avatar = IMG(_src=logo,
                 _height=50,
                 _width=50,
                 _style="padding-right:5px;",
                 _class="media-object")
    avatar = A(avatar,
               _href=org_url,
               _class="pull-left",
               )

    # Edit Bar
    permit = current.auth.s3_has_permission
    if permit("update", table, record_id=record_id):
        edit_btn = A(I(" ", _class="icon icon-edit"),
                     _href=URL(c="cms", f="post",
                               args=[record_id, "update.popup"],
                               #vars={"refresh": listid,
                               #      "record": record_id}
                               ),
                     _class="s3_modal",
                     _title=T("Edit %(type)s") % dict(type=T(series)),
                     )
    else:
        edit_btn = ""
    if permit("delete", table, record_id=record_id):
        delete_btn = A(I(" ", _class="icon icon-remove-sign"),
                       _class="dl-item-delete",
                       )
    else:
        delete_btn = ""
    edit_bar = DIV(edit_btn,
                   delete_btn,
                   _class="edit-bar fright",
                   )

    # Dropdown of available documents
    dtable = db.doc_document
    query = (table.doc_id == dtable.doc_id) & \
            (dtable.deleted == False)
    documents = db(query).select(dtable.file) 
    if documents:
        doc_list = UL(_class="dropdown-menu",
                      _role="menu",
                      )
        retrieve = db.doc_document.file.retrieve
        for doc in documents:
            filename = doc.file
            try:
                doc_name = retrieve(filename)[0]
            except IOError:
                doc_name = current.messages["NONE"]
            doc_url = URL(c="default", f="download",
                          args=[filename])
            doc_item = LI(A(I(_class="icon-file"),
                            " ",
                            doc_name,
                            _href=doc_url,
                            ),
                          _role="menuitem",
                          )
            doc_list.append(doc_item)
        docs = DIV(A(I(_class="icon-paper-clip"),
                     SPAN(_class="caret"),
                     _class="btn dropdown-toggle",
                     _href="#",
                     **{"_data-toggle": "dropdown"}
                     ),
                   doc_list,
                   _class="btn-group attachments dropdown pull-right",
                   )
    else:
        docs = ""

    icon = series.lower().replace(" ", "_")
    card_label = TAG[""](I(_class="icon icon-%s" % icon),
                         SPAN(" %s" % T(series),
                              _class="card-title"))
    # Type cards
    if series == "Incident": 
        # Apply additional highlighting for Incidents
        item_class = "%s disaster" % item_class

    # Render the item
    item = DIV(DIV(card_label,
                   SPAN(A(location,
                          _href=location_url,
                          ),
                        _class="location-title",
                        ),
                   SPAN(date,
                        _class="date-title",
                        ),
                   #edit_bar,
                   _class="card-header",
                   ),
               DIV(avatar,
                   DIV(DIV(body,
                           DIV(author,
                               " - ",
                               A(organisation,
                                 _href=org_url,
                                 _class="card-organisation",
                                 ),
                               _class="card-person",
                               ),
                           _class="media",
                           ),
                       _class="media-body",
                       ),
                   _class="media",
                   ),
               docs,
               _class=item_class,
               _id=item_id,
               )

    return item
    
# =============================================================================
def cms_post_age(row):
    """
        The age of the post
        - used for colour-coding markers of Incidents
    """

    if hasattr(row, "cms_post"):
        row = row.cms_post
    try:
        date = row.date
    except:
        # not available
        return current.messages["NONE"]

    now = current.request.utcnow
    age = now - date
    if age < timedelta(days=2):
        return 1
    elif age < timedelta(days=7):
        return 2
    else:
        return 3

# -----------------------------------------------------------------------------
def customize_cms_post(**attr):
    """
        Customize cms_post controller
    """

    s3db = current.s3db
    s3 = current.response.s3

    #s3db.configure("cms_post",
    #               marker_fn=cms_post_marker_fn,
    #               )

    # Custom PreP
    standard_prep = s3.prep
    def custom_prep(r):
        # Call standard prep
        if callable(standard_prep):
            # Called first so that we can unhide the Type field
            result = standard_prep(r)
            if not result:
                return False

        if r.interactive:
            from s3.s3forms import S3SQLCustomForm, S3SQLInlineComponent
            table = customize_cms_post_fields()

            get_vars = current.request.get_vars

            field = table.series_id
            field.label = T("Type")
            
            if r.method == "read":
                # Restore the label for the Location
                table.location_id.label = T("Location")

            refresh = get_vars.get("refresh", None)
            if refresh == "datalist":
                # We must be coming from the News Feed page so can change the type on-the-fly
                field.readable = field.writable = True
            #field.requires = field.requires.other
            #field = table.name
            #field.readable = field.writable = False
            #field = table.title
            #field.readable = field.writable = False
            field = table.avatar
            field.default = True
            #field.readable = field.writable = False
            field = table.replies
            field.default = False
            #field.readable = field.writable = False
            
            field = table.body
            field.label = T("Description")
            field.widget = None
            #table.comments.readable = table.comments.writable = False

            if current.request.controller == "default":
                # Don't override card layout for News Feed/Homepage
                return True

            # Filter from a Profile page?
            # If so, then default the fields we know
            location_id = get_vars.get("~.(location)", None)
            if location_id:
                table.location_id.default = location_id
            # event_id = get_vars.get("~.(event)", None)
            # if event_id:
                # crud_form = S3SQLCustomForm(
                    # "date",
                    # "series_id",
                    # "body",
                    # "location_id",
                    # S3SQLInlineComponent(
                        # "document",
                        # name = "file",
                        # label = T("Files"),
                        # fields = ["file",
                                  ##"comments",
                                  # ],
                    # ),
                # )
                # def create_onaccept(form):
                    # table = current.s3db.event_event_post
                    # table.insert(event_id=event_id, post_id=form.vars.id)

                # s3db.configure("cms_post",
                               # create_onaccept = create_onaccept, 
                               # )
            # else:
            crud_form = S3SQLCustomForm(
                "date",
                "series_id",
                "body",
                "location_id",
                #S3SQLInlineComponent(
                #    "event_post",
                #    #label = T("Disaster(s)"),
                #    label = T("Disaster"),
                #    multiple = False,
                #    fields = ["event_id"],
                #    orderby = "event_id$name",
                #),
                S3SQLInlineComponent(
                    "document",
                    name = "file",
                    label = T("Files"),
                    fields = ["file",
                              #"comments",
                              ],
                ),
            )

            # Return to List view after create/update/delete
            # We now do all this in Popups
            #url_next = URL(c="default", f="index", args="newsfeed")

            s3db.configure("cms_post",
                           #create_next = url_next,
                           #delete_next = url_next,
                           #update_next = url_next,
                           crud_form = crud_form,
                           # Don't include a Create form in 'More' popups
                           listadd = False,
                           list_layout = render_posts,
                           )

            s3.cancel = True
        elif r.representation == "xls":
            table = r.table
            table.created_by.represent = s3_auth_user_represent_name
            #table.created_on.represent = datetime_represent
            utable = current.auth.settings.table_user
            utable.organisation_id.represent = s3db.org_organisation_represent

            list_fields = [
                (T("Date"), "date"),
                (T("Disaster"), "event_post.event_id"),
                (T("Type"), "series_id"),
                (T("Details"), "body"),
                (T("District"), "location_id$L1"),
                (T("Sub-District"), "location_id$L2"),
                (T("Suco"), "location_id$L3"),
                (T("Author"), "created_by"),
                (T("Organization"), "created_by$organisation_id"),
                ]
            s3db.configure("cms_post",
                           list_fields = list_fields,
                           )

        elif r.representation == "plain" and \
             r.method != "search":
            # Map Popups
            table = r.table
            table.location_id.represent = s3db.gis_LocationRepresent(sep=" | ")
            table.created_by.represent = s3_auth_user_represent_name
            # Used by default popups
            series = T(table.series_id.represent(r.record.series_id))
            s3.crud_strings["cms_post"].title_display = "%(series)s Details" % dict(series=series)
            s3db.configure("cms_post",
                           popup_url="",
                           )
            table.avatar.readable = False
            table.body.label = ""
            table.expired.readable = False
            table.replies.readable = False
            table.created_by.readable = True
            table.created_by.label = T("Author")
            # Used by cms_post_popup
            #table.created_on.represent = datetime_represent

        elif r.representation == "geojson":
            r.table.age = Field.Lazy(cms_post_age)

        return True
    s3.prep = custom_prep

    # Custom postp
    standard_postp = s3.postp
    def custom_postp(r, output):
        # Call standard postp
        if callable(standard_postp):
            output = standard_postp(r, output)

        if r.interactive and isinstance(output, dict):
            if "form" in output:
                output["form"].add_class("cms_post")
            elif "item" in output and hasattr(output["item"], "add_class"):
                output["item"].add_class("cms_post")
        elif r.representation == "plain" and \
             r.method != "search":
            # Map Popups
            #output = cms_post_popup(r)
            pass

        return output
    s3.postp = custom_postp

    return attr

settings.ui.customize_cms_post = customize_cms_post

# -----------------------------------------------------------------------------
def customize_event_event(**attr):
    """
        Customize event_event controller
        - Profile Page
    """

    s3 = current.response.s3

    # Custom PreP
    standard_prep = s3.prep
    def custom_prep(r):
        if r.interactive:
            ADD_EVENT = T("New Disaster")
            s3.crud_strings["event_event"] = Storage(
                title_create = ADD_EVENT,
                title_display = T("Disaster Details"),
                title_list = T("Disasters"),
                title_update = T("Edit Disaster"),
                title_search = T("Search Disasters"),
                subtitle_create = T("Add New Disaster"),
                label_list_button = T("List Disasters"),
                label_create_button = ADD_EVENT,
                label_delete_button = T("Delete Disaster"),
                msg_record_created = T("Disaster added"),
                msg_record_modified = T("Disaster updated"),
                msg_record_deleted = T("Disaster deleted"),
                msg_list_empty = T("No Disasters currently registered"))
            
            db = current.db
            s3db = current.s3db

            # Load normal Model
            table = s3db.event_event

            table.exercise.label = T("Is this an Exercise?")
            table.zero_hour.label = T("Start Time")

            if r.method =="datalist":
                # Disaster selection page
                # 2-column datalist, 6 rows per page
                s3.dl_pagelength = 12
                s3.dl_rowsize = 2

            elif r.method == "profile":
                # Customise the cms_post table as that is used for the widgets
                customize_cms_post_fields()

                # Represent used in rendering
                current.auth.settings.table_user.organisation_id.represent = s3db.org_organisation_represent

                gtable = db.gis_location
                ltable = db.event_event_location
                query = (ltable.event_id == r.id) & \
                        (ltable.location_id == gtable.id)
                location = db(query).select(gtable.id,
                                            gtable.lat_max,
                                            gtable.lon_max,
                                            gtable.lat_min,
                                            gtable.lon_min,
                                            limitby=(0, 1)).first()
                if location:
                    bbox = {"lat_max" : location.lat_max,
                            "lon_max" : location.lon_max,
                            "lat_min" : location.lat_min,
                            "lon_min" : location.lon_min
                            }
                    default = "~.(location)=%s" % location.id
                else:
                    # Default bounds
                    bbox = {}
                    # No default Location
                    default = None
                map_widget = dict(label = "Map",
                                  type = "map",
                                  context = "event",
                                  icon = "icon-map",
                                  height = 383,
                                  width = 568,
                                  bbox = bbox,
                                  )
                incidents_widget = dict(label = "Incidents",
                                        title_create = "Add New Incident",
                                        type = "datalist",
                                        tablename = "cms_post",
                                        context = "event",
                                        default = default,
                                        filter = S3FieldSelector("series_id$name") == "Incident",
                                        icon = "icon-incident",
                                        layer = "Incidents",
                                        # provided by Catalogue Layer
                                        #marker = "incident",
                                        list_layout = render_profile_posts,
                                        )
                assessments_widget = dict(label = "Assessments",
                                          title_create = "Add New Assessment",
                                          type = "datalist",
                                          tablename = "cms_post",
                                          context = "event",
                                          default = default,
                                          filter = S3FieldSelector("series_id$name") == "Assessment",
                                          icon = "icon-assessment",
                                          layer = "Assessments",
                                          # provided by Catalogue Layer
                                          #marker = "assessment",
                                          list_layout = render_profile_posts,
                                          )
                activities_widget = dict(label = "Activities",
                                         title_create = "Add New Activity",
                                         type = "datalist",
                                         tablename = "cms_post",
                                         context = "event",
                                         default = default,
                                         filter = S3FieldSelector("series_id$name") == "Activity",
                                         icon = "icon-activity",
                                         layer = "Activities",
                                         # provided by Catalogue Layer
                                         #marker = "activity",
                                         list_layout = render_profile_posts,
                                         )
                reports_widget = dict(label = "Reports",
                                      title_create = "Add New Report",
                                      type = "datalist",
                                      tablename = "cms_post",
                                      context = "event",
                                      default = default,
                                      filter = S3FieldSelector("series_id$name") == "Report",
                                      icon = "icon-report",
                                      layer = "Reports",
                                      # provided by Catalogue Layer
                                      #marker = "report",
                                      list_layout = render_profile_posts,
                                      )
                #comments_widget = dict(label = "Comments",
                #                       type = "comments",
                #                       icon = "icon-comments-alt",
                #                       colspan = 2,
                #                       )
                record = r.record
                ttable = db.event_event_type
                event_type = db(ttable.id == record.event_type_id).select(ttable.name,
                                                                          limitby=(0, 1),
                                                                          ).first().name
                s3db.configure("event_event",
                               profile_title = "%s : %s" % (s3.crud_strings["event_event"].title_list, 
                                                            record.name),
                               profile_header = DIV(A(IMG(_class="media-object",
                                                          _src=URL(c="static",
                                                                   f="themes",
                                                                   args=["DRMP", "img",
                                                                         "%s.png" % event_type]),
                                                          ),
                                                      _class="pull-left",
                                                      #_href=event_url,
                                                      ),
                                                    H2(record.name),
                                                    #P(record.comments),
                                                    _class="profile_header",
                                                    ),
                               profile_widgets = [incidents_widget,
                                                  map_widget,
                                                  assessments_widget,
                                                  activities_widget,
                                                  reports_widget,
                                                  #comments_widget,
                                                  ])

            # Include a Location inline
            location_field = s3db.event_event_location.location_id
            # Don't label a single field InlineComponent
            location_field.label = ""
            represent = S3Represent(lookup="gis_location")
            location_field.represent = represent
            # L1s only
            location_field.requires = IS_NULL_OR(
                                        IS_ONE_OF(db, "gis_location.id",
                                                  represent,
                                                  sort = True,
                                                  filterby = "level",
                                                  filter_opts = ["L1"]
                                                  )
                                        )
            # Don't add new Locations here
            location_field.comment = None
            # Simple dropdown
            location_field.widget = None

            from s3.s3forms import S3SQLCustomForm, S3SQLInlineComponent
            crud_form = S3SQLCustomForm(
                    "name",
                    "event_type_id",
                    "exercise",
                    "zero_hour",
                    "closed",
                    S3SQLInlineComponent(
                        "event_location",
                        label = T("District"),
                        multiple = False,
                        fields = ["location_id"],
                    ),
                    "comments",
                )
            
            s3db.configure("event_event",
                           create_next = URL(c="event", f="event",
                                             args=["[id]", "profile"]),
                           crud_form = crud_form,
                           # We want the Create form to be in a modal, not inline, for consistency
                           listadd = False,
                           list_layout = render_events,
                           )

        # Call standard prep
        if callable(standard_prep):
            result = standard_prep(r)
            if not result:
                return False

        return True
    s3.prep = custom_prep

    # Custom postp
    standard_postp = s3.postp
    def custom_postp(r, output):
        if r.interactive and \
           current.auth.s3_has_permission("create", r.table):
            # Insert a Button to Create New in Modal
            output["showadd_btn"] = A(I(_class="icon icon-plus-sign big-add"),
                                      _href=URL(c="event", f="event",
                                                args=["create.popup"],
                                                vars={"refresh": "datalist"}),
                                      _class="btn btn-primary s3_modal",
                                      _role="button",
                                      _title=T("Add New Disaster"),
                                      )

        # Call standard postp
        if callable(standard_postp):
            output = standard_postp(r, output)

        return output
    s3.postp = custom_postp

    return attr

settings.ui.customize_event_event = customize_event_event

# -----------------------------------------------------------------------------
def customize_gis_location(**attr):
    """
        Customize gis_location controller
        - Profile Page
    """

    s3 = current.response.s3

    # Custom PreP
    standard_prep = s3.prep
    def custom_prep(r):
        if r.interactive:
            s3db = current.s3db
            table = s3db.gis_location

            s3.crud_strings["gis_location"].title_list = T("Countries")

            if r.method == "datalist":
                # District selection page
                # 2-column datalist, 6 rows per page
                s3.dl_pagelength = 12
                s3.dl_rowsize = 2

                # Just show specific Countries
                s3.filter = (table.name.belongs("Syrian Arab Republic", "Jordan", "Iraq", "Lebanon", "Turkey"))
                # Default 5 triggers an AJAX call, we should load all by default
                s3.dl_pagelength = 13

                list_fields = ["name",
                               "level",
                               "L1",
                               "L2",
                               "L3",
                               ]
                s3db.configure("gis_location",
                               list_fields = list_fields,
                               list_layout = render_locations,
                               )

            elif r.method == "profile":
        
                # Customise tables used by widgets
                customize_cms_post_fields()
                customize_project_project_fields()

                # gis_location table (Sub-Locations)
                table.parent.represent = s3db.gis_LocationRepresent(sep=" | ")

                list_fields = ["name",
                               "id",
                               ]

                # Represent used in rendering
                current.auth.settings.table_user.organisation_id.represent = s3db.org_organisation_represent

                location = r.record
                record_id = location.id
                default = "~.(location)=%s" % record_id
                map_widget = dict(label = "Map",
                                  type = "map",
                                  context = "location",
                                  icon = "icon-map",
                                  height = 383,
                                  width = 568,
                                  bbox = {"lat_max" : location.lat_max,
                                          "lon_max" : location.lon_max,
                                          "lat_min" : location.lat_min,
                                          "lon_min" : location.lon_min
                                          },
                                  )
                #locations_widget = dict(label = "Locations",
                #                        insert = False,
                #                        #title_create = "Add New Location",
                #                        type = "datalist",
                #                        tablename = "gis_location",
                #                        context = "location",
                #                        icon = "icon-globe",
                #                        # @ToDo: Show as Polygons?
                #                        show_on_map = False,
                #                        list_layout = render_locations_profile,
                #                        )
                incidents_widget = dict(label = "Incidents",
                                        title_create = "Add New Incident",
                                        type = "datalist",
                                        tablename = "cms_post",
                                        context = "location",
                                        default = default,
                                        filter = (S3FieldSelector("series_id$name") == "Incident") & (S3FieldSelector("expired") == False),
                                        icon = "icon-incident",
                                        layer = "Incidents",
                                        # provided by Catalogue Layer
                                        #marker = "incident",
                                        list_layout = render_profile_posts,
                                        )
                projects_widget = dict(label = "Projects",
                                       title_create = "Add New Project",
                                       type = "datalist",
                                       tablename = "project_project",
                                       context = "location",
                                       default = default,
                                       icon = "icon-project",
                                       show_on_map = False, # No Marker yet & only show at L1-level anyway
                                       list_layout = render_projects,
                                       )
                reports_widget = dict(label = "Reports",
                                      title_create = "Add New Report",
                                      type = "datalist",
                                      tablename = "cms_post",
                                      context = "location",
                                      default = default,
                                      filter = S3FieldSelector("series_id$name") == "Report",
                                      icon = "icon-report",
                                      layer = "Reports",
                                      # provided by Catalogue Layer
                                      #marker = "report",
                                      list_layout = render_profile_posts,
                                      )
                # @ToDo: Renderer
                #distributions_widget = dict(label = "Distributions",
                #                            title_create = "Add New Distribution",
                #                            type = "datalist",
                #                            tablename = "supply_distribution",
                #                            context = "location",
                #                            default = default,
                #                            icon = "icon-resource",
                #                            list_layout = render_distributions,
                #                            )
                # Build the icon, if it doesn't already exist
                filename = "%s.svg" % record_id
                import os
                filepath = os.path.join(current.request.folder, "static", "cache", "svg", filename)
                if not os.path.exists(filepath):
                    gtable = db.gis_location
                    loc = db(gtable.id == record_id).select(gtable.wkt,
                                                            limitby=(0, 1)
                                                            ).first()
                    if loc:
                        from s3.codecs.svg import S3SVG
                        S3SVG.write_file(filename, loc.wkt)

                name = location.name
                s3db.configure("gis_location",
                               list_fields = list_fields,
                               profile_title = "%s : %s" % (s3.crud_strings["gis_location"].title_list, 
                                                            name),
                               profile_header = DIV(A(IMG(_class="media-object",
                                                          _src=URL(c="static",
                                                                   f="cache",
                                                                   args=["svg", filename],
                                                                   ),
                                                          ),
                                                      _class="pull-left",
                                                      #_href=location_url,
                                                      ),
                                                    H2(name),
                                                    _class="profile_header",
                                                    ),
                               profile_widgets = [#locations_widget,
                                                  incidents_widget,
                                                  map_widget,
                                                  projects_widget,
                                                  reports_widget,
                                                  #activities_widget,
                                                  #distributions_widget,
                                                  ],
                               )

        # Call standard prep
        if callable(standard_prep):
            result = standard_prep(r)
            if not result:
                return False

        return True
    s3.prep = custom_prep

    return attr

settings.ui.customize_gis_location = customize_gis_location

# -----------------------------------------------------------------------------
def customize_hrm_human_resource_fields():
    """
        Customize hrm_human_resource for Profile widgets and 'more' popups
    """

    s3db = current.s3db
    table = s3db.hrm_human_resource
    table.site_id.represent = S3Represent(lookup="org_site")
    s3db.org_site.location_id.represent = s3db.gis_LocationRepresent(sep=" | ")
    #table.modified_by.represent = s3_auth_user_represent_name
    table.modified_on.represent = datetime_represent

    list_fields = ["person_id",
                   "person_id$pe_id",
                   "organisation_id",
                   "site_id$location_id",
                   "site_id$location_id$addr_street",
                   "job_title_id",
                   "email.value",
                   "phone.value",
                   #"modified_by",
                   "modified_on",
                   ]

    s3db.configure("hrm_human_resource",
                   list_fields = list_fields,
                   )

# -----------------------------------------------------------------------------
def customize_hrm_human_resource(**attr):
    """
        Customize hrm_human_resource controller
        - used for 'more' popups
    """

    s3 = current.response.s3

    # Custom PreP
    standard_prep = s3.prep
    def custom_prep(r):
        # Call standard prep
        if callable(standard_prep):
            result = standard_prep(r)
            if not result:
                return False

        if r.method == "datalist":
            customize_hrm_human_resource_fields()
            current.s3db.configure("hrm_human_resource",
                                   # Don't include a Create form in 'More' popups
                                   listadd = False,
                                   list_layout = render_contacts,
                                   )

        return True
    s3.prep = custom_prep

    return attr

settings.ui.customize_hrm_human_resource = customize_hrm_human_resource

# -----------------------------------------------------------------------------
def customize_hrm_job_title(**attr):
    """
        Customize hrm_job_title controller
    """

    s3 = current.response.s3

    table = current.s3db.hrm_job_title
    
    # Configure fields
    field = table.organisation_id
    field.readable = field.writable = False
    field.default = None
    
    # Custom postp
    standard_postp = s3.postp
    def custom_postp(r, output):
        if r.interactive:
            actions = [dict(label=str(T("Open")),
                            _class="action-btn",
                            url=URL(c="hrm", f="job_title",
                                    args=["[id]", "read"]))
                       ]
            db = current.db
            auth = current.auth
            has_permission = auth.s3_has_permission
            ownership_required = auth.permission.ownership_required
            s3_accessible_query = auth.s3_accessible_query
            if has_permission("update", table):
                action = dict(label=str(T("Edit")),
                              _class="action-btn",
                              url=URL(c="hrm", f="job_title",
                                      args=["[id]", "update"]),
                              )
                if ownership_required("update", table):
                    # Check which records can be updated
                    query = s3_accessible_query("update", table)
                    rows = db(query).select(table._id)
                    restrict = []
                    rappend = restrict.append
                    for row in rows:
                        row_id = row.get("id", None)
                        if row_id:
                            rappend(str(row_id))
                    action["restrict"] = restrict
                actions.append(action)
            if has_permission("delete", table):
                action = dict(label=str(T("Delete")),
                              _class="action-btn",
                              url=URL(c="hrm", f="job_title",
                                      args=["[id]", "delete"]),
                              )
                if ownership_required("delete", table):
                    # Check which records can be deleted
                    query = s3_accessible_query("delete", table)
                    rows = db(query).select(table._id)
                    restrict = []
                    rappend = restrict.append
                    for row in rows:
                        row_id = row.get("id", None)
                        if row_id:
                            rappend(str(row_id))
                    action["restrict"] = restrict
                actions.append(action)
            s3.actions = actions
            if isinstance(output, dict):
                if "form" in output:
                    output["form"].add_class("hrm_job_title")
                elif "item" in output and hasattr(output["item"], "add_class"):
                    output["item"].add_class("hrm_job_title")

        # Call standard postp
        if callable(standard_postp):
            output = standard_postp(r, output)

        return output
    s3.postp = custom_postp

    return attr

settings.ui.customize_hrm_job_title = customize_hrm_job_title

# -----------------------------------------------------------------------------
def customize_org_office_fields():
    """
        Customize org_office for Profile widgets and 'more' popups
    """

    s3db = current.s3db
    table = s3db.org_office
    table.location_id.represent = s3db.gis_LocationRepresent(sep=" | ")
    table.modified_by.represent = s3_auth_user_represent_name
    table.modified_on.represent = datetime_represent

    list_fields = ["name",
                   "organisation_id",
                   "office_type_id",
                   "location_id",
                   "location_id$addr_street",
                   "modified_by",
                   "modified_on",
                   "organisation_id$logo",
                   ]

    s3db.configure("org_office",
                   list_fields = list_fields,
                   )

# -----------------------------------------------------------------------------
def customize_org_office(**attr):
    """
        Customize org_office controller
    """

    s3 = current.response.s3
    s3db = current.s3db
    table = s3db.org_office
    
    # Custom PreP
    standard_prep = s3.prep
    def custom_prep(r):
        # Call standard prep
        if callable(standard_prep):
            result = standard_prep(r)
            if not result:
                return False

        if r.method == "datalist":
            customize_org_office_fields()
            s3db.configure("org_office",
                           # Don't include a Create form in 'More' popups
                           listadd = False,
                           list_layout = render_offices,
                           )

        elif r.interactive or r.representation == "aadata":
            # Configure fields
            table.code.readable = table.code.writable = False
            #table.office_type_id.readable = table.office_type_id.writable = False
            table.phone1.readable = table.phone1.writable = False
            table.phone2.readable = table.phone2.writable = False
            table.email.readable = table.email.writable = False
            table.fax.readable = table.fax.writable = False
            location_field = table.location_id

            # Filter from a Profile page?
            # If so, then default the fields we know
            get_vars = current.request.get_vars
            location_id = get_vars.get("~.(location)", None)
            organisation_id = get_vars.get("~.(organisation)", None)
            if organisation_id:
                org_field = table.organisation_id
                org_field.default = organisation_id
                org_field.readable = org_field.writable = False
            if location_id:
                location_field.default = location_id
                location_field.readable = location_field.writable = False
            else:
                # Don't add new Locations here
                location_field.comment = None
                # L1s only
                location_field.requires = IS_LOCATION_SELECTOR2(levels=["L0", "L1"])
                location_field.widget = S3LocationSelectorWidget2(levels=["L0", "L1"],
                                                                  show_address=True,
                                                                  show_map=False)
            s3.cancel = True

        return True
    s3.prep = custom_prep

    # Custom postp
    standard_postp = s3.postp
    def custom_postp(r, output):
        if r.interactive:
            actions = [dict(label=str(T("Open")),
                            _class="action-btn",
                            url=URL(c="org", f="office",
                                    args=["[id]", "read"]))
                       ]
            db = current.db
            auth = current.auth
            has_permission = auth.s3_has_permission
            ownership_required = auth.permission.ownership_required
            s3_accessible_query = auth.s3_accessible_query
            if has_permission("update", table):
                action = dict(label=str(T("Edit")),
                              _class="action-btn",
                              url=URL(c="org", f="office",
                                      args=["[id]", "update"]),
                              )
                if ownership_required("update", table):
                    # Check which records can be updated
                    query = s3_accessible_query("update", table)
                    rows = db(query).select(table._id)
                    restrict = []
                    rappend = restrict.append
                    for row in rows:
                        row_id = row.get("id", None)
                        if row_id:
                            rappend(str(row_id))
                    action["restrict"] = restrict
                actions.append(action)
            if has_permission("delete", table):
                action = dict(label=str(T("Delete")),
                              _class="action-btn",
                              url=URL(c="org", f="office",
                                      args=["[id]", "delete"]),
                              )
                if ownership_required("delete", table):
                    # Check which records can be deleted
                    query = s3_accessible_query("delete", table)
                    rows = db(query).select(table._id)
                    restrict = []
                    rappend = restrict.append
                    for row in rows:
                        row_id = row.get("id", None)
                        if row_id:
                            rappend(str(row_id))
                    action["restrict"] = restrict
                actions.append(action)
            s3.actions = actions
            if isinstance(output, dict):
                if "form" in output:
                    output["form"].add_class("org_office")
                elif "item" in output and hasattr(output["item"], "add_class"):
                    output["item"].add_class("org_office")

        # Call standard postp
        if callable(standard_postp):
            output = standard_postp(r, output)

        return output
    s3.postp = custom_postp

    return attr

settings.ui.customize_org_office = customize_org_office

# -----------------------------------------------------------------------------
def customize_org_organisation(**attr):
    """
        Customize org_organisation controller
        - Profile Page
    """

    s3 = current.response.s3

    # Custom PreP
    standard_prep = s3.prep
    def custom_prep(r):
        # Call standard prep
        if callable(standard_prep):
            result = standard_prep(r)
            if not result:
                return False

        if r.interactive:
            # ADD_ORGANISATION = T("New Stakeholder")
            # s3.crud_strings["org_organisation"] = Storage(
                # title_create = ADD_ORGANISATION,
                # title_display = T("Stakeholder Details"),
                # title_list = T("Stakeholders"),
                # title_update = T("Edit Stakeholder"),
                # title_search = T("Search Stakeholders"),
                # subtitle_create = T("Add New Stakeholder"),
                # label_list_button = T("List Stakeholders"),
                # label_create_button = ADD_ORGANISATION,
                # label_delete_button = T("Delete Stakeholder"),
                # msg_record_created = T("Stakeholder added"),
                # msg_record_modified = T("Stakeholder updated"),
                # msg_record_deleted = T("Stakeholder deleted"),
                # msg_list_empty = T("No Stakeholders currently registered"))

            list_fields = ["id",
                           "name",
                           "logo",
                           "phone",
                           ]

            s3db = current.s3db
            if r.method == "profile":
                # Customise tables used by widgets
                customize_cms_post_fields()
                customize_hrm_human_resource_fields()
                customize_org_office_fields()
                customize_project_project_fields()

                contacts_widget = dict(label = "Contacts",
                                       title_create = "Add New Contact",
                                       type = "datalist",
                                       tablename = "hrm_human_resource",
                                       context = "organisation",
                                       create_controller = "pr",
                                       create_function = "person",
                                       icon = "icon-contact",
                                       show_on_map = False, # Since they will show within Offices
                                       list_layout = render_contacts,
                                       )
                map_widget = dict(label = "Map",
                                  type = "map",
                                  context = "organisation",
                                  icon = "icon-map",
                                  height = 383,
                                  width = 568,
                                  )
                offices_widget = dict(label = "Offices",
                                      title_create = "Add New Office",
                                      type = "datalist",
                                      tablename = "org_office",
                                      context = "organisation",
                                      icon = "icon-home",
                                      layer = "Offices",
                                      # provided by Catalogue Layer
                                      #marker = "office",
                                      list_layout = render_offices,
                                      )
                projects_widget = dict(label = "Projects",
                                       title_create = "Add New Project",
                                       type = "datalist",
                                       tablename = "project_project",
                                       context = "organisation",
                                       icon = "icon-project",
                                       show_on_map = False, # No Marker yet & only show at L1-level anyway
                                       list_layout = render_projects,
                                       )
                reports_widget = dict(label = "Reports",
                                      title_create = "Add New Report",
                                      type = "datalist",
                                      tablename = "cms_post",
                                      context = "organisation",
                                      filter = S3FieldSelector("series_id$name") == "Report",
                                      icon = "icon-report",
                                      layer = "Reports",
                                      # provided by Catalogue Layer
                                      #marker = "report",
                                      list_layout = render_profile_posts,
                                      )
                assessments_widget = dict(label = "Assessments",
                                          title_create = "Add New Assessment",
                                          type = "datalist",
                                          tablename = "cms_post",
                                          context = "organisation",
                                          filter = S3FieldSelector("series_id$name") == "Assessment",
                                          icon = "icon-assessment",
                                          layer = "Assessments",
                                          # provided by Catalogue Layer
                                          #marker = "assessment",
                                          list_layout = render_profile_posts,
                                          )
                # @ToDo: Renderer
                #distributions_widget = dict(label = "Distributions",
                #                            title_create = "Add New Distribution",
                #                            type = "datalist",
                #                            tablename = "supply_distribution",
                #                            context = "location",
                #                            default = default,
                #                            icon = "icon-resource",
                #                            list_layout = render_distributions,
                #                            )
                record = r.record
                s3db.configure("org_organisation",
                               profile_title = "%s : %s" % (s3.crud_strings["org_organisation"].title_list, 
                                                            record.name),
                               profile_header = DIV(A(IMG(_class="media-object",
                                                          _src=URL(c="default", f="download",
                                                                   args=[record.logo]),
                                                          ),
                                                      _class="pull-left",
                                                      #_href=org_url,
                                                      ),
                                                    H2(record.name),
                                                    _class="profile_header",
                                                    ),
                               profile_widgets = [contacts_widget,
                                                  map_widget,
                                                  offices_widget,
                                                  projects_widget,
                                                  #activities_widget,
                                                  reports_widget,
                                                  assessments_widget,
                                                  #distributions_widget,
                                                  ]
                               )
            elif r.method == "datalist":
                # Stakeholder selection page
                # 2-column datalist, 6 rows per page
                s3.dl_pagelength = 12
                s3.dl_rowsize = 2

                # Add a component of just National offices for the Org address
                ottable = s3db.org_office_type
                query = (ottable.name == "National")
                national = current.db(query).select(ottable.id,
                                                    limitby=(0, 1)
                                                    ).first().id
                s3db.add_component("org_office",
                                   org_organisation=dict(name="nat_office",
                                                         joinby="organisation_id",
                                                         filterby="office_type_id",
                                                         filterfor=[national],
                                                         ))
                list_fields.append("nat_office.location_id$addr_street")

            # Represent used in rendering
            current.auth.settings.table_user.organisation_id.represent = s3db.org_organisation_represent

            # Load normal Model
            table = s3db.org_organisation

            # Hide fields
            table.organisation_type_id.readable = table.organisation_type_id.writable = False
            table.region.readable = table.region.writable = False
            table.country.readable = table.country.writable = False
            table.year.readable = table.year.writable = False
            
            # Return to List view after create/update/delete (unless done via Modal)
            url_next = URL(c="org", f="organisation", args="datalist")

            s3db.configure("org_organisation",
                           create_next = url_next,
                           delete_next = url_next,
                           update_next = url_next,
                           # We want the Create form to be in a modal, not inline, for consistency
                           listadd = False,
                           list_fields = list_fields,
                           list_layout = render_organisations,
                           )

        return True
    s3.prep = custom_prep

    # Custom postp
    standard_postp = s3.postp
    def custom_postp(r, output):
        if r.interactive and \
           isinstance(output, dict) and \
           current.auth.s3_has_permission("create", r.table):
            # Insert a Button to Create New in Modal
            output["showadd_btn"] = A(I(_class="icon icon-plus-sign big-add"),
                                      _href=URL(c="org", f="organisation",
                                                args=["create.popup"],
                                                vars={"refresh": "datalist"}),
                                      _class="btn btn-primary s3_modal",
                                      _role="button",
                                      _title=T("Add New Organization"),
                                      )

        # Call standard postp
        if callable(standard_postp):
            output = standard_postp(r, output)

        return output
    s3.postp = custom_postp

    return attr

settings.ui.customize_org_organisation = customize_org_organisation

# -----------------------------------------------------------------------------
def customize_pr_person(**attr):
    """
        Customize pr_person controller
    """

    s3db = current.s3db
    s3 = current.response.s3

    tablename = "pr_person"
    table = s3db.pr_person

    # Custom PreP
    standard_prep = s3.prep
    def custom_prep(r):
        # Call standard prep
        if callable(standard_prep):
            result = standard_prep(r)
            if not result:
                return False

        if r.method == "validate":
            # Can't validate image without the file
            image_field = s3db.pr_image.image
            image_field.requires = None

        if r.interactive or r.representation == "aadata":
            from s3.s3forms import S3SQLCustomForm, S3SQLInlineComponent
            # CRUD Strings
            ADD_CONTACT = T("Add New Contact")
            s3.crud_strings[tablename] = Storage(
                title_create = T("Add Contact"),
                title_display = T("Contact Details"),
                title_list = T("Contact Directory"),
                title_update = T("Edit Contact Details"),
                title_search = T("Search Contacts"),
                subtitle_create = ADD_CONTACT,
                label_list_button = T("List Contacts"),
                label_create_button = ADD_CONTACT,
                label_delete_button = T("Delete Contact"),
                msg_record_created = T("Contact added"),
                msg_record_modified = T("Contact details updated"),
                msg_record_deleted = T("Contact deleted"),
                msg_list_empty = T("No Contacts currently registered"))

            MOBILE = settings.get_ui_label_mobile_phone()
            EMAIL = T("Email")

            htable = s3db.hrm_human_resource
            htable.organisation_id.widget = None
            site_field = htable.site_id
            represent = S3Represent(lookup="org_site")
            site_field.represent = represent
            site_field.requires = IS_ONE_OF(current.db, "org_site.site_id",
                                            represent,
                                            orderby = "org_site.name")
            from s3layouts import S3AddResourceLink
            site_field.comment = S3AddResourceLink(c="org", f="office",
                                                   vars={"child": "site_id"},
                                                   label=T("Add New Office"),
                                                   title=T("Office"),
                                                   tooltip=T("If you don't see the Office in the list, you can add a new one by clicking link 'Add New Office'."))

            # Best to have no labels when only 1 field in the row
            s3db.pr_contact.value.label = ""
            image_field = s3db.pr_image.image
            image_field.label = ""
            # ImageCrop widget doesn't currently work within an Inline Form
            image_field.widget = None

            hr_fields = ["organisation_id",
                         "job_title_id",
                         "site_id",
                         ]
            if r.method in ("create", "update"):
                # Context from a Profile page?"
                organisation_id = current.request.get_vars.get("(organisation)", None)
                if organisation_id:
                    field = s3db.hrm_human_resource.organisation_id
                    field.default = organisation_id
                    field.readable = field.writable = False
                    hr_fields.remove("organisation_id")

            s3_sql_custom_fields = [
                    "first_name",
                    #"middle_name",
                    "last_name",
                    S3SQLInlineComponent(
                        "human_resource",
                        name = "human_resource",
                        label = "",
                        multiple = False,
                        fields = hr_fields,
                    ),
                    S3SQLInlineComponent(
                        "image",
                        name = "image",
                        label = T("Photo"),
                        multiple = False,
                        fields = ["image"],
                    ),
                ]

            list_fields = [(current.messages.ORGANISATION, "human_resource.organisation_id"),
                           "first_name",
                           #"middle_name",
                           "last_name",
                           (T("Job Title"), "human_resource.job_title_id"),
                           (T("Office"), "human_resource.site_id"),
                           ]
            
            # Don't include Email/Phone for unauthenticated users
            if current.auth.is_logged_in():
                list_fields += [(MOBILE, "phone.value"),
                                (EMAIL, "email.value"),
                                ]
                s3_sql_custom_fields.insert(3,
                                            S3SQLInlineComponent(
                                            "contact",
                                            name = "phone",
                                            label = MOBILE,
                                            multiple = False,
                                            fields = ["value"],
                                            filterby = dict(field = "contact_method",
                                                            options = "SMS")),
                                            )
                s3_sql_custom_fields.insert(3,
                                            S3SQLInlineComponent(
                                            "contact",
                                            name = "email",
                                            label = EMAIL,
                                            multiple = False,
                                            fields = ["value"],
                                            filterby = dict(field = "contact_method",
                                                            options = "EMAIL")),
                                            )

            crud_form = S3SQLCustomForm(*s3_sql_custom_fields)

            # Return to List view after create/update/delete (unless done via Modal)
            url_next = URL(c="pr", f="person")

            s3db.configure(tablename,
                           create_next = url_next,
                           delete_next = url_next,
                           update_next = url_next,
                           crud_form = crud_form,
                           list_fields = list_fields,
                           # Don't include a Create form in 'More' popups
                           listadd = False if r.method=="datalist" else True,
                           list_layout = render_contacts,
                           )

            # Move fields to their desired Locations
            # Disabled as breaks submission of inline_component
            #i18n = []
            #iappend = i18n.append
            #iappend('''i18n.office="%s"''' % T("Office"))
            #iappend('''i18n.organisation="%s"''' % T("Organization"))
            #iappend('''i18n.job_title="%s"''' % T("Job Title"))
            #i18n = '''\n'''.join(i18n)
            #s3.js_global.append(i18n)
            #s3.scripts.append('/%s/static/themes/DRMP/js/contacts.js' % current.request.application)

        return True
    s3.prep = custom_prep

    # Custom postp
    standard_postp = s3.postp
    def custom_postp(r, output):
        # Call standard postp
        if callable(standard_postp):
            output = standard_postp(r, output)

        if r.interactive and isinstance(output, dict):
            output["rheader"] = ""
            actions = [dict(label=str(T("Open")),
                            _class="action-btn",
                            url=URL(c="pr", f="person",
                                    args=["[id]", "read"]))
                       ]
            # All users just get "Open"
            #db = current.db
            #auth = current.auth
            #has_permission = auth.s3_has_permission
            #ownership_required = auth.permission.ownership_required
            #s3_accessible_query = auth.s3_accessible_query
            #if has_permission("update", table):
            #    action = dict(label=str(T("Edit")),
            #                  _class="action-btn",
            #                  url=URL(c="pr", f="person",
            #                          args=["[id]", "update"]),
            #                  )
            #    if ownership_required("update", table):
            #        # Check which records can be updated
            #        query = s3_accessible_query("update", table)
            #        rows = db(query).select(table._id)
            #        restrict = []
            #        rappend = restrict.append
            #        for row in rows:
            #            row_id = row.get("id", None)
            #            if row_id:
            #                rappend(str(row_id))
            #        action["restrict"] = restrict
            #    actions.append(action)
            #if has_permission("delete", table):
            #    action = dict(label=str(T("Delete")),
            #                  _class="action-btn",
            #                  url=URL(c="pr", f="person",
            #                          args=["[id]", "delete"]),
            #                  )
            #    if ownership_required("delete", table):
            #        # Check which records can be deleted
            #        query = s3_accessible_query("delete", table)
            #        rows = db(query).select(table._id)
            #        restrict = []
            #        rappend = restrict.append
            #        for row in rows:
            #            row_id = row.get("id", None)
            #            if row_id:
            #                rappend(str(row_id))
            #        action["restrict"] = restrict
            #    actions.append(action)
            s3.actions = actions
            if "form" in output:
                output["form"].add_class("pr_person")
            elif "item" in output and hasattr(output["item"], "add_class"):
                output["item"].add_class("pr_person")

        return output
    s3.postp = custom_postp

    return attr

settings.ui.customize_pr_person = customize_pr_person

# -----------------------------------------------------------------------------
def customize_project_project_fields():
    """
        Customize project_project fields for Profile widgets and 'more' popups
    """

    format = "%d/%m/%y"
    date_represent = lambda d: S3DateTime.date_represent(d, format=format)

    s3db = current.s3db

    s3db.project_location.location_id.represent = s3db.gis_LocationRepresent(sep=" | ")
    table = s3db.project_project
    table.start_date.represent = date_represent
    table.end_date.represent = date_represent
    table.modified_by.represent = s3_auth_user_represent_name
    table.modified_on.represent = datetime_represent

    list_fields = [#"name",
                   "organisation_id",
                   "location.location_id",
                   "organisation_id$logo",
                   "start_date",
                   "end_date",
                   #"human_resource_id",
                   "budget",
                   "partner.organisation_id",
                   "donor.organisation_id",
                   "donor.amount",
                   "donor.currency",
                   "modified_by",
                   "modified_on",
                   "document.file",
                   ]

    s3db.configure("project_project",
                   list_fields = list_fields,
                   )

# -----------------------------------------------------------------------------
def customize_project_project(**attr):
    """
        Customize project_project controller
    """

    s3 = current.response.s3

    # Remove rheader
    attr["rheader"] = None

    # Custom PreP
    standard_prep = s3.prep
    def custom_prep(r):
        # Call standard prep
        if callable(standard_prep):
            result = standard_prep(r)
            if not result:
                return False

        s3db = current.s3db
        table = s3db.project_project

        if r.method == "datalist":
            customize_project_project_fields()
            s3db.configure("project_project",
                           # Don't include a Create form in 'More' popups
                           listadd = False,
                           list_layout = render_projects,
                           )
        elif r.interactive or r.representation == "aadata":
            # Filter from a Profile page?
            # If so, then default the fields we know
            get_vars = current.request.get_vars
            organisation_id = get_vars.get("~.(organisation)", None)
            if not organisation_id:
                user = current.auth.user
                if user:
                    organisation_id = user.organisation_id

            # Configure fields 
            table.objectives.readable = table.objectives.writable = True
            from s3.s3widgets import S3AddPersonWidget2
            table.human_resource_id.label = T("Focal Person")
            table.human_resource_id.widget = S3AddPersonWidget2()
            s3db.hrm_human_resource.organisation_id.default = organisation_id
            table.budget.label = "%s (USD)" % T("Budget")
            # Better in column label & otherwise this construction loses thousands separators
            #table.budget.represent = lambda value: "%d USD" % value

            s3db.doc_document.file.label = ""

            crud_form_fields = [
                    "name",
                    S3SQLInlineComponentCheckbox(
                        "theme",
                        label = T("Themes"),
                        field = "theme_id",
                        option_help = "comments",
                        cols = 3,
                    ),
                    S3SQLInlineComponent(
                        "location",
                        label = T("Districts"),
                        fields = ["location_id"],
                        orderby = "location_id$name",
                        render_list = True
                    ),
                    "description",
                    "human_resource_id",
                    "start_date",
                    "end_date",
                    # Partner Orgs
                    S3SQLInlineComponent(
                        "organisation",
                        name = "partner",
                        label = T("Partner Organizations"),
                        fields = ["organisation_id",
                                  ],
                        filterby = dict(field = "role",
                                        options = "2"
                                        )
                    ),
                    # Donors
                    S3SQLInlineComponent(
                        "organisation",
                        name = "donor",
                        label = T("Donor(s)"),
                        fields = ["organisation_id", "amount", "currency"],
                        filterby = dict(field = "role",
                                        options = "3"
                                        )
                    ),
                    "budget",
                    #"objectives",
                    # Files
                    S3SQLInlineComponent(
                        "document",
                        name = "file",
                        label = T("Files"),
                        fields = ["file",
                                  #"comments"
                                  ],
                    ),
                    "comments",
                    ]
            if organisation_id:
                org_field = table.organisation_id
                org_field.default = organisation_id
                org_field.readable = org_field.writable = False
            else:
                location_field = s3db.project_location.location_id
                location_id = get_vars.get("~.(location)", None)
                if location_id:
                    # Default to this Location, but allow selection of others
                    location_field.default = location_id
                location_field.label = ""
                location_field.represent = S3Represent(lookup="gis_location")
                # Project Locations must be districts
                location_field.requires = IS_ONE_OF(current.db, "gis_location.id",
                                                    S3Represent(lookup="gis_location"),
                                                    sort = True,
                                                    filterby = "level",
                                                    filter_opts = ["L1"]
                                                    )
                # Don't add new Locations here
                location_field.comment = None
                # Simple dropdown
                location_field.widget = None
                crud_form_fields.insert(1, "organisation_id")

            crud_form = S3SQLCustomForm(*crud_form_fields)

            list_fields = [#"name",
                           "organisation_id",
                           "human_resource_id",
                           (T("Districts"), "location.location_id"),
                           "start_date",
                           "end_date",
                           #"budget",
                           ]

            # Return to List view after create/update/delete (unless done via Modal)
            url_next = URL(c="project", f="project")

            from s3.s3filter import S3LocationFilter, S3TextFilter, S3OptionsFilter
            filter_widgets = [
                S3TextFilter(["name",
                              "description",
                              "location.location_id",
                              #"theme.name",
                              #"objectives",
                              "comments"
                              ],
                             label = T("Search Projects"),
                             ),
                S3OptionsFilter("organisation_id",
                                label = T("Lead Organisation"),
                                widget="multiselect"
                                ),
                S3LocationFilter("location.location_id",
                                 levels=["L0", "L1", "L2", "L3"],
                                 widget="multiselect"),
                S3OptionsFilter("partner.organisation_id",
                                label = T("Partners"),
                                widget="multiselect"),
                S3OptionsFilter("donor.organisation_id",
                                label = T("Donors"),
                                widget="multiselect")
                ]

            s3db.configure("project_project",
                           create_next = url_next,
                           delete_next = url_next,
                           update_next = url_next,
                           crud_form = crud_form,
                           list_fields = list_fields,
                           filter_widgets = filter_widgets,
                           )

            s3.cancel = True

        return True
    s3.prep = custom_prep

    # Custom postp
    standard_postp = s3.postp
    def custom_postp(r, output):
        if r.interactive:
            actions = [dict(label=str(T("Open")),
                            _class="action-btn",
                            url=URL(c="project", f="project",
                                    args=["[id]", "read"]))
                       ]
            # All users just get "Open"
            #db = current.db
            #auth = current.auth
            #has_permission = auth.s3_has_permission
            #ownership_required = auth.permission.ownership_required
            #s3_accessible_query = auth.s3_accessible_query
            #if has_permission("update", table):
            #    action = dict(label=str(T("Edit")),
            #                  _class="action-btn",
            #                  url=URL(c="project", f="project",
            #                          args=["[id]", "update"]),
            #                  )
            #    if ownership_required("update", table):
            #        # Check which records can be updated
            #        query = s3_accessible_query("update", table)
            #        rows = db(query).select(table._id)
            #        restrict = []
            #        rappend = restrict.append
            #        for row in rows:
            #            row_id = row.get("id", None)
            #            if row_id:
            #                rappend(str(row_id))
            #        action["restrict"] = restrict
            #    actions.append(action)
            #if has_permission("delete", table):
            #    action = dict(label=str(T("Delete")),
            #                  _class="action-btn",
            #                  url=URL(c="project", f="project",
            #                          args=["[id]", "delete"]),
            #                  )
            #    if ownership_required("delete", table):
            #        # Check which records can be deleted
            #        query = s3_accessible_query("delete", table)
            #        rows = db(query).select(table._id)
            #        restrict = []
            #        rappend = restrict.append
            #        for row in rows:
            #            row_id = row.get("id", None)
            #            if row_id:
            #                rappend(str(row_id))
            #        action["restrict"] = restrict
            #    actions.append(action)
            s3.actions = actions
            if isinstance(output, dict):
                if "form" in output:
                    output["form"].add_class("project_project")
                elif "item" in output and hasattr(output["item"], "add_class"):
                    output["item"].add_class("project_project")

        # Call standard postp
        if callable(standard_postp):
            output = standard_postp(r, output)

        return output
    s3.postp = custom_postp

    #attr["hide_filter"] = False

    return attr

settings.ui.customize_project_project = customize_project_project

# -----------------------------------------------------------------------------
def customize_project_beneficiary(**attr):
    """
        Customize project_beneficiary controller
    """

    s3 = current.response.s3

    # Remove rheader
    attr["rheader"] = None

    # Custom PreP
    standard_prep = s3.prep
    def custom_prep(r):
        # Call standard prep
        if callable(standard_prep):
            result = standard_prep(r)
            if not result:
                return False

        s3db = current.s3db
        table = s3db.project_beneficiary

        from s3.s3filter import S3LocationFilter, S3OptionsFilter
        filter_widgets = [
            S3LocationFilter("location_id",
                             levels=["L0", "L1", "L2", "L3"],
                             widget="multiselect"),
            S3OptionsFilter("project_id$sector_project.sector_id",
                            label = T("Sector"),
                            widget="multiselect"
                            ),
            S3OptionsFilter("parameter_id",
                            label = T("Beneficiary Type"),
                            widget="multiselect"
                            ),
            # @ToDo: Range Slider using start_date & end_date
            #S3DateFilter("date",
            #             )
            #S3OptionsFilter("project_id$organisation_id",
            #                label = T("Lead Organisation"),
            #                widget="multiselect"
            #                ),
            ]

        report_fields = [(T("Beneficiary Type"), "parameter_id"),
                         "project_id$sector_project.sector_id",
                         (T("Year"), "year"),
                         (current.messages.COUNTRY, "location_id$L0"),
                         "location_id$L1",
                         "location_id$L2",
                         "location_id$L3",
                         ]

        report_options = Storage(
            rows=report_fields,
            cols=report_fields,
            fact=[("sum(value)", T("Number of Beneficiaries"))],
            defaults=Storage(rows="location_id$L1",
                             cols="parameter_id",
                             fact="sum(value)",
                             totals=True,
                             #chart = "barchart:rows",
                             #table = "collapse",
                             )
            )

        s3db.configure("project_beneficiary",
                       #list_fields = list_fields,
                       filter_widgets = filter_widgets,
                       # For Summary View
                       #filter_formstyle = filter_formstyle,
                       report_options = report_options,
                       )

        s3.cancel = True

        return True
    s3.prep = custom_prep

    # Custom postp
    standard_postp = s3.postp
    def custom_postp(r, output):
        if r.interactive:
            actions = [dict(label=str(T("Open")),
                            _class="action-btn",
                            url=URL(c="project", f="beneficiary",
                                    args=["[id]", "read"]))
                       ]
            # All users just get "Open"
            #db = current.db
            #auth = current.auth
            #has_permission = auth.s3_has_permission
            #ownership_required = auth.permission.ownership_required
            #s3_accessible_query = auth.s3_accessible_query
            #if has_permission("update", table):
            #    action = dict(label=str(T("Edit")),
            #                  _class="action-btn",
            #                  url=URL(c="project", f="project",
            #                          args=["[id]", "update"]),
            #                  )
            #    if ownership_required("update", table):
            #        # Check which records can be updated
            #        query = s3_accessible_query("update", table)
            #        rows = db(query).select(table._id)
            #        restrict = []
            #        rappend = restrict.append
            #        for row in rows:
            #            row_id = row.get("id", None)
            #            if row_id:
            #                rappend(str(row_id))
            #        action["restrict"] = restrict
            #    actions.append(action)
            #if has_permission("delete", table):
            #    action = dict(label=str(T("Delete")),
            #                  _class="action-btn",
            #                  url=URL(c="project", f="project",
            #                          args=["[id]", "delete"]),
            #                  )
            #    if ownership_required("delete", table):
            #        # Check which records can be deleted
            #        query = s3_accessible_query("delete", table)
            #        rows = db(query).select(table._id)
            #        restrict = []
            #        rappend = restrict.append
            #        for row in rows:
            #            row_id = row.get("id", None)
            #            if row_id:
            #                rappend(str(row_id))
            #        action["restrict"] = restrict
            #    actions.append(action)
            s3.actions = actions
            if isinstance(output, dict):
                if "form" in output:
                    output["form"].add_class("project_beneficiary")
                elif "item" in output and hasattr(output["item"], "add_class"):
                    output["item"].add_class("project_beneficiary")

        # Call standard postp
        if callable(standard_postp):
            output = standard_postp(r, output)

        return output
    s3.postp = custom_postp

    attr["hide_filter"] = False

    return attr

settings.ui.customize_project_beneficiary = customize_project_beneficiary

# -----------------------------------------------------------------------------
def customize_doc_document(**attr):
    """
        Customize doc_document controller
    """

    s3 = current.response.s3
    s3db = current.s3db
    tablename = "doc_document"
    table = s3db.doc_document

    # Custom PreP
    standard_prep = s3.prep
    def custom_prep(r):
        # Call standard prep
        if callable(standard_prep):
            result = standard_prep(r)

        # Filter Out Docs from Newsfeed
        current.response.s3.filter = (table.name != None)

        if r.interactive:
            s3.crud_strings[tablename] = Storage(
                title_create = T("Add Document"),
                title_display = T("Document"),
                title_list = T("Documents"),
                title_update = T("Edit Document"),
                title_search = T("Search Documents"),
                subtitle_create = T("Add Document"),
                label_list_button = T("List New Documents"),
                label_create_button = T("Add Documents"),
                label_delete_button = T("Remove Documents"),
                msg_record_created = T("Documents added"),
                msg_record_modified = T("Documents updated"),
                msg_record_deleted = T("Documents removed"),
                msg_list_empty = T("No Documents currently recorded"))

            # Force added docs to have a name
            table.name.requires = IS_NOT_EMPTY()

            list_fields = ["name",
                           "file",
                           "url",
                           "organisation_id",
                           "comments",
                           ]

            crud_form = S3SQLCustomForm(*list_fields)

            s3db.configure(tablename,
                           list_fields = list_fields,
                           crud_form = crud_form,
                           )
        return True
    s3.prep = custom_prep

    return attr

settings.ui.customize_doc_document = customize_doc_document

# -----------------------------------------------------------------------------
# Filter forms - style for Summary pages
def filter_formstyle(row_id, label, widget, comment, hidden=False):
    return DIV(label, widget, comment, 
               _id=row_id,
               _class="horiz_filter_form")

# =============================================================================
# Template Modules
# Comment/uncomment modules here to disable/enable them
settings.modules = OrderedDict([
    # Core modules which shouldn't be disabled
    ("default", Storage(
        name_nice = "Home",
        restricted = False, # Use ACLs to control access to this module
        access = None,      # All Users (inc Anonymous) can see this module in the default menu & access the controller
        module_type = None  # This item is not shown in the menu
    )),
    ("admin", Storage(
        name_nice = "Administration",
        #description = "Site Administration",
        restricted = True,
        access = "|1|",     # Only Administrators can see this module in the default menu & access the controller
        module_type = None  # This item is handled separately for the menu
    )),
    ("appadmin", Storage(
        name_nice = "Administration",
        #description = "Site Administration",
        restricted = True,
        module_type = None  # No Menu
    )),
    ("errors", Storage(
        name_nice = "Ticket Viewer",
        #description = "Needed for Breadcrumbs",
        restricted = False,
        module_type = None  # No Menu
    )),
    ("sync", Storage(
        name_nice = "Synchronization",
        #description = "Synchronization",
        restricted = True,
        access = "|1|",     # Only Administrators can see this module in the default menu & access the controller
        module_type = None  # This item is handled separately for the menu
    )),
    ("translate", Storage(
        name_nice = "Translation Functionality",
        #description = "Selective translation of strings based on module.",
        module_type = None,
    )),
    ("gis", Storage(
        name_nice = "Map",
        #description = "Situation Awareness & Geospatial Analysis",
        restricted = True,
        module_type = 1,     # 1st item in the menu
    )),
    ("pr", Storage(
        name_nice = "Persons",
        #description = "Central point to record details on People",
        restricted = True,
        access = "|1|",     # Only Administrators can see this module in the default menu (access to controller is possible to all still)
        module_type = None
    )),
    ("org", Storage(
        name_nice = "Organizations",
        #description = 'Lists "who is doing what & where". Allows relief agencies to coordinate their activities',
        restricted = True,
        module_type = None
    )),
    # All modules below here should be possible to disable safely
    ("hrm", Storage(
        name_nice = "Contacts",
        #description = "Human Resources Management",
        restricted = True,
        module_type = None,
    )),
    ("cms", Storage(
            name_nice = "Content Management",
            restricted = True,
            module_type = None,
        )),
    ("doc", Storage(
        name_nice = "Documents",
        #description = "A library of digital resources, such as photos, documents and reports",
        restricted = True,
        module_type = None,
    )),
    ("msg", Storage(
        name_nice = "Messaging",
        #description = "Sends & Receives Alerts via Email & SMS",
        restricted = True,
        # The user-visible functionality of this module isn't normally required. Rather it's main purpose is to be accessed from other modules.
        module_type = None,
    )),
    ("event", Storage(
        name_nice = "Disasters",
        #description = "Events",
        restricted = True,
        module_type = None
    )),
    ("project", Storage(
        name_nice = "Projects",
        restricted = True,
        module_type = None
    )),
    ("stats", Storage(
        name_nice = "Statistics",
        restricted = True,
        module_type = None
    )),
    ("vulnerability", Storage(
        name_nice = "Vulnerability",
        restricted = True,
        module_type = None
    )),
    ("transport", Storage(
        name_nice = "Transport",
        restricted = True,
        module_type = None
    )),
    ("hms", Storage(
        name_nice = "Hospitals",
        restricted = True,
        module_type = None
    )),
    ("cr", Storage(
        name_nice = "Shelters",
        restricted = True,
        module_type = None
    )),
    ("supply", Storage(
        name_nice = "Supply Chain Management",
        restricted = True,
        module_type = None
    )),
])
